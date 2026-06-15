import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import UserRole


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateRoleRequest(BaseModel):
    role: UserRole
