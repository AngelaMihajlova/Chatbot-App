import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import GroupRole


class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None


class GroupResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class GroupMemberResponse(BaseModel):
    user_id: uuid.UUID
    group_id: uuid.UUID
    role: GroupRole
    email: str
    username: Optional[str]

    model_config = {"from_attributes": True}


class AddMemberRequest(BaseModel):
    user_id: uuid.UUID


class AssignDocumentRequest(BaseModel):
    document_id: uuid.UUID
