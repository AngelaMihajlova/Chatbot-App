from typing import Literal, Optional

from pydantic import BaseModel


class SystemSettings(BaseModel):
    STORAGE_BACKEND: Literal["minio", "s3"] = "minio"
    DYNAMO_MODE: Literal["local", "aws"] = "local"


class UpdateSettingsRequest(BaseModel):
    STORAGE_BACKEND: Optional[Literal["minio", "s3"]] = None
    DYNAMO_MODE: Optional[Literal["local", "aws"]] = None
