from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models import SystemConfig, User, UserRole


def init_db(db: Session) -> None:
    # Migrate: add is_public column if the documents table already exists without it
    try:
        db.execute(text(
            "ALTER TABLE documents ADD COLUMN IF NOT EXISTS is_public BOOLEAN NOT NULL DEFAULT FALSE"
        ))
        db.commit()
    except Exception:
        db.rollback()

    superadmin = db.query(User).filter(User.email == settings.SUPERADMIN_EMAIL).first()
    if not superadmin:
        db.add(User(
            email=settings.SUPERADMIN_EMAIL,
            username=settings.SUPERADMIN_USERNAME,
            hashed_password=get_password_hash(settings.SUPERADMIN_PASSWORD),
            role=UserRole.superadmin,
            is_active=True,
        ))

    defaults = {
        "STORAGE_BACKEND": "minio",
        "DYNAMO_MODE": "local",
    }
    for key, value in defaults.items():
        if not db.query(SystemConfig).filter(SystemConfig.key == key).first():
            db.add(SystemConfig(key=key, value=value))

    db.commit()
