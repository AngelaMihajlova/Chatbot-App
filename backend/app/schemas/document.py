import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import DocumentStatus


class DocumentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    original_filename: str
    mimetype: str
    size: int
    status: DocumentStatus
    error_message: Optional[str]
    is_public: bool
    uploaded_by: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
