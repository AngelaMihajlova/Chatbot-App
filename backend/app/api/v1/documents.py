import uuid
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_admin, require_superadmin
from app.db.models import Document, DocumentStatus, User
from app.db.session import SessionLocal
from app.schemas.document import DocumentResponse
from app.services import access as access_svc
from app.services import storage as storage_svc
from app.services import vector as vector_svc
from app.services import ingest as ingest_svc

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_MIMETYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/x-markdown",
    "text/csv",
}


def _ingest_background(document_id: str, filename: str, s3_key: str, mimetype: str) -> None:
    db = SessionLocal()
    try:
        content = storage_svc.download_file(db, s3_key)
        count = ingest_svc.ingest_document(document_id, filename, s3_key, content, mimetype)
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = DocumentStatus.indexed
            db.commit()
    except Exception as exc:
        db.rollback()
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = DocumentStatus.error
            doc.error_message = str(exc)[:500]
            db.commit()
    finally:
        db.close()


@router.get("", response_model=List[DocumentResponse])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    return access_svc.get_visible_documents_for_admin(current_user, db)


@router.patch("/{document_id}/public", response_model=DocumentResponse)
def toggle_public(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.is_public = not doc.is_public
    db.commit()
    db.refresh(doc)
    return doc


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_MIMETYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {content_type}")

    content = await file.read()
    doc_id = uuid.uuid4()
    s3_key = f"{doc_id}/{file.filename}"

    storage_svc.upload_file(db, s3_key, content, content_type)

    doc = Document(
        id=doc_id,
        filename=file.filename,
        original_filename=file.filename,
        s3_key=s3_key,
        mimetype=content_type,
        size=len(content),
        status=DocumentStatus.pending,
        uploaded_by=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    background_tasks.add_task(_ingest_background, str(doc_id), file.filename, s3_key, content_type)
    return doc


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    vector_svc.delete_document_chunks(str(document_id))
    storage_svc.delete_file(db, doc.s3_key)
    db.delete(doc)
    db.commit()


@router.post("/{document_id}/sync", response_model=DocumentResponse)
def sync_document(
    document_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    vector_svc.delete_document_chunks(str(document_id))
    doc.status = DocumentStatus.pending
    doc.error_message = None
    db.commit()
    db.refresh(doc)
    background_tasks.add_task(_ingest_background, str(document_id), doc.filename, doc.s3_key, doc.mimetype)
    return doc
