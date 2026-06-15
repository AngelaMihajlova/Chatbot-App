from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_superadmin
from app.db.models import SystemConfig, User
from app.schemas.settings import SystemSettings, UpdateSettingsRequest

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SystemSettings)
def get_settings(db: Session = Depends(get_db), _: User = Depends(require_superadmin)):
    rows = db.query(SystemConfig).all()
    cfg = {r.key: r.value for r in rows}
    return SystemSettings(**cfg)


@router.patch("", response_model=SystemSettings)
def update_settings(
    req: UpdateSettingsRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_superadmin),
):
    updates = req.model_dump(exclude_none=True)
    for key, value in updates.items():
        row = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if row:
            row.value = value
            row.updated_at = datetime.utcnow()
        else:
            db.add(SystemConfig(key=key, value=value))
    db.commit()
    rows = db.query(SystemConfig).all()
    return SystemSettings(**{r.key: r.value for r in rows})
