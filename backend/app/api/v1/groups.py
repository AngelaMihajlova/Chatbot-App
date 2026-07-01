import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_admin, require_superadmin
from app.db.models import Document, DocumentGroup, Group, GroupRole, User, UserGroup, UserRole
from app.schemas.document import DocumentResponse
from app.schemas.group import (
    AddMemberRequest,
    AssignDocumentRequest,
    GroupCreate,
    GroupMemberResponse,
    GroupResponse,
)
from app.services import access as access_svc
from app.services.realtime import manager as ws_manager

router = APIRouter(prefix="/groups", tags=["groups"])


# ── Group CRUD (superadmin only) ──────────────────────────────────────────────

@router.get("", response_model=List[GroupResponse])
def list_groups(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if current_user.role == UserRole.superadmin:
        return db.query(Group).order_by(Group.name).all()
    admin_ids = access_svc.get_admin_group_ids(current_user, db)
    return db.query(Group).filter(Group.id.in_(admin_ids)).order_by(Group.name).all()


@router.post("", response_model=GroupResponse, status_code=201)
def create_group(req: GroupCreate, db: Session = Depends(get_db), _: User = Depends(require_superadmin)):
    if db.query(Group).filter(Group.name == req.name).first():
        raise HTTPException(status_code=400, detail="Group name already exists")
    group = Group(name=req.name, description=req.description)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.delete("/{group_id}", status_code=204)
def delete_group(group_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_superadmin)):
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    db.delete(group)
    db.commit()


# ── Members ───────────────────────────────────────────────────────────────────

@router.get("/{group_id}/members", response_model=List[GroupMemberResponse])
def list_members(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    access_svc.require_group_admin(group_id, current_user, db)
    rows = db.query(UserGroup).filter(UserGroup.group_id == group_id).all()
    return [
        GroupMemberResponse(
            user_id=r.user_id,
            group_id=r.group_id,
            role=r.role,
            email=r.user.email,
            username=r.user.username,
        )
        for r in rows
    ]


@router.post("/{group_id}/members", response_model=GroupMemberResponse, status_code=201)
def add_member(
    group_id: uuid.UUID,
    req: AddMemberRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    access_svc.require_group_admin(group_id, current_user, db)

    if not db.query(Group).filter(Group.id == group_id).first():
        raise HTTPException(status_code=404, detail="Group not found")
    target = db.query(User).filter(User.id == req.user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if db.query(UserGroup).filter(UserGroup.user_id == req.user_id, UserGroup.group_id == group_id).first():
        raise HTTPException(status_code=400, detail="User already in group")

    initial_role = GroupRole.admin if target.role in (UserRole.admin, UserRole.superadmin) else GroupRole.member
    membership = UserGroup(user_id=req.user_id, group_id=group_id, role=initial_role)
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return GroupMemberResponse(
        user_id=membership.user_id,
        group_id=membership.group_id,
        role=membership.role,
        email=target.email,
        username=target.username,
    )


@router.patch("/{group_id}/members/{user_id}/promote", response_model=GroupMemberResponse)
def promote_to_admin(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    membership = db.query(UserGroup).filter(
        UserGroup.group_id == group_id, UserGroup.user_id == user_id
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    membership.role = GroupRole.admin
    promoted_globally = membership.user.role == UserRole.user
    if promoted_globally:
        membership.user.role = UserRole.admin
    db.commit()
    db.refresh(membership)
    if promoted_globally:
        ws_manager.notify(str(membership.user.id), {"type": "role_updated", "role": membership.user.role.value})
    return GroupMemberResponse(
        user_id=membership.user_id,
        group_id=membership.group_id,
        role=membership.role,
        email=membership.user.email,
        username=membership.user.username,
    )


@router.delete("/{group_id}/members/{user_id}", status_code=204)
def remove_member(
    group_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    access_svc.require_group_admin(group_id, current_user, db)
    membership = db.query(UserGroup).filter(
        UserGroup.group_id == group_id, UserGroup.user_id == user_id
    ).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    db.delete(membership)
    db.commit()


# ── Documents ─────────────────────────────────────────────────────────────────

@router.get("/{group_id}/documents", response_model=List[DocumentResponse])
def list_group_documents(
    group_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    access_svc.require_group_admin(group_id, current_user, db)
    rows = db.query(DocumentGroup).filter(DocumentGroup.group_id == group_id).all()
    return [r.document for r in rows]


@router.post("/{group_id}/documents", response_model=DocumentResponse, status_code=201)
def assign_document(
    group_id: uuid.UUID,
    req: AssignDocumentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    access_svc.require_group_admin(group_id, current_user, db)

    doc = db.query(Document).filter(Document.id == req.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Group admins can only assign docs they uploaded or that are already in their groups
    if current_user.role != UserRole.superadmin:
        accessible = access_svc.get_accessible_doc_ids(current_user, db) or []
        if str(doc.id) not in accessible and str(doc.uploaded_by) != str(current_user.id):
            raise HTTPException(status_code=403, detail="No access to this document")

    if db.query(DocumentGroup).filter(
        DocumentGroup.document_id == req.document_id, DocumentGroup.group_id == group_id
    ).first():
        raise HTTPException(status_code=400, detail="Document already in group")

    db.add(DocumentGroup(document_id=req.document_id, group_id=group_id))
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{group_id}/documents/{document_id}", status_code=204)
def remove_document(
    group_id: uuid.UUID,
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    access_svc.require_group_admin(group_id, current_user, db)
    dg = db.query(DocumentGroup).filter(
        DocumentGroup.group_id == group_id, DocumentGroup.document_id == document_id
    ).first()
    if not dg:
        raise HTTPException(status_code=404, detail="Document not in group")
    db.delete(dg)
    db.commit()
