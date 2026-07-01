import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_admin, require_superadmin
from app.db.models import GroupRole, User, UserGroup, UserRole
from app.schemas.user import UpdateRoleRequest, UserResponse
from app.services.realtime import manager as ws_manager

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return db.query(User).order_by(User.created_at).all()


@router.patch("/{user_id}/role", response_model=UserResponse)
def update_role(
    user_id: uuid.UUID,
    req: UpdateRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in (UserRole.admin, UserRole.superadmin):
        raise HTTPException(status_code=403, detail="Admin access required")

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.role == UserRole.superadmin:
        raise HTTPException(status_code=403, detail="Cannot modify superadmin")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot change your own role")
    if req.role == UserRole.superadmin:
        raise HTTPException(status_code=403, detail="Cannot grant superadmin role")
    if current_user.role == UserRole.admin and target.role == UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins cannot modify other admins")

    role_changed = target.role != req.role
    target.role = req.role
    if req.role == UserRole.admin:
        for membership in db.query(UserGroup).filter(UserGroup.user_id == target.id).all():
            membership.role = GroupRole.admin
    elif req.role == UserRole.user:
        for membership in db.query(UserGroup).filter(UserGroup.user_id == target.id).all():
            membership.role = GroupRole.member
    db.commit()
    db.refresh(target)
    if role_changed:
        ws_manager.notify(str(target.id), {"type": "role_updated", "role": target.role.value})
    return target


@router.patch("/{user_id}/toggle-active", response_model=UserResponse)
def toggle_active(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.role == UserRole.superadmin:
        raise HTTPException(status_code=403, detail="Cannot deactivate superadmin")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    if current_user.role == UserRole.admin and target.role == UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins cannot deactivate other admins")
    target.is_active = not target.is_active
    db.commit()
    db.refresh(target)
    return target


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.role == UserRole.superadmin:
        raise HTTPException(status_code=403, detail="Cannot delete superadmin")
    if target.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    if current_user.role == UserRole.admin and target.role == UserRole.admin:
        raise HTTPException(status_code=403, detail="Admins cannot delete other admins")
    db.delete(target)
    db.commit()
