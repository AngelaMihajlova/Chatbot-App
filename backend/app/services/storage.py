from botocore.client import Config
from botocore.config import Config as BotoConfig
import boto3

_BOTO_TIMEOUT = BotoConfig(connect_timeout=5, read_timeout=10, retries={"max_attempts": 1})
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import SystemConfig


def _get_backend(db: Session) -> str:
    row = db.query(SystemConfig).filter(SystemConfig.key == "STORAGE_BACKEND").first()
    return row.value if row else "minio"


def get_storage_client(db: Session):
    backend = _get_backend(db)
    if backend == "s3":
        client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            config=_BOTO_TIMEOUT,
        )
        return client, settings.AWS_S3_BUCKET
    client = boto3.client(
        "s3",
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4", connect_timeout=5, read_timeout=10, retries={"max_attempts": 1}),
        region_name="us-east-1",
    )
    return client, settings.MINIO_BUCKET


def upload_file(db: Session, key: str, data: bytes, content_type: str) -> None:
    client, bucket = get_storage_client(db)
    client.put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)


def download_file(db: Session, key: str) -> bytes:
    client, bucket = get_storage_client(db)
    return client.get_object(Bucket=bucket, Key=key)["Body"].read()


def delete_file(db: Session, key: str) -> None:
    client, bucket = get_storage_client(db)
    client.delete_object(Bucket=bucket, Key=key)


def ensure_bucket(db: Session) -> None:
    if _get_backend(db) != "minio":
        return
    client, bucket = get_storage_client(db)
    existing = [b["Name"] for b in client.list_buckets().get("Buckets", [])]
    if bucket not in existing:
        client.create_bucket(Bucket=bucket)
