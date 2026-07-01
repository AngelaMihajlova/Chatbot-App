from fastapi import APIRouter

from app.api.v1 import auth, chat, documents, groups, settings, users, ws

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(documents.router)
router.include_router(groups.router)
router.include_router(chat.router)
router.include_router(settings.router)
router.include_router(ws.router)
