from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.models import Document, DocumentGroup, Group, GroupRole, User, UserGroup, UserRole


def get_accessible_doc_ids(user: User, db: Session) -> Optional[list]:
    """Returns None for superadmin (no filter), or list of accessible doc ID strings."""
    if user.role == UserRole.superadmin:
        return None

    public = db.query(Document.id).filter(Document.is_public.is_(True))
    in_groups = (
        db.query(Document.id)
        .join(DocumentGroup, DocumentGroup.document_id == Document.id)
        .join(UserGroup, UserGroup.group_id == DocumentGroup.group_id)
        .filter(UserGroup.user_id == user.id)
    )
    rows = public.union(in_groups).all()
    return [str(r[0]) for r in rows]


def get_admin_group_ids(user: User, db: Session) -> list:
    """Returns group IDs where the user has admin role."""
    rows = (
        db.query(UserGroup.group_id)
        .filter(UserGroup.user_id == user.id, UserGroup.role == GroupRole.admin)
        .all()
    )
    return [str(r[0]) for r in rows]


def require_group_admin(group_id: UUID, user: User, db: Session) -> None:
    if user.role == UserRole.superadmin:
        return
    membership = db.query(UserGroup).filter(
        UserGroup.user_id == user.id,
        UserGroup.group_id == group_id,
        UserGroup.role == GroupRole.admin,
    ).first()
    if not membership:
        raise HTTPException(status_code=403, detail="Not an admin of this group")


def get_visible_documents_for_admin(user: User, db: Session):
    """Documents visible in the admin panel: uploaded by user OR in their admin groups."""
    if user.role == UserRole.superadmin:
        return db.query(Document).all()
    uploaded = db.query(Document.id).filter(Document.uploaded_by == user.id)
    in_admin_groups = (
        db.query(Document.id)
        .join(DocumentGroup, DocumentGroup.document_id == Document.id)
        .join(UserGroup, UserGroup.group_id == DocumentGroup.group_id)
        .filter(UserGroup.user_id == user.id, UserGroup.role == GroupRole.admin)
    )
    ids = [r[0] for r in uploaded.union(in_admin_groups).all()]
    return db.query(Document).filter(Document.id.in_(ids)).order_by(Document.created_at.desc()).all()
