from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import SessionLocal
from app.services.realtime import manager

router = APIRouter(tags=["ws"])


@router.websocket("/ws")
async def account_updates(websocket: WebSocket, token: str = Query(...)):
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008)
        return

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == payload["sub"]).first()
    finally:
        db.close()
    if not user or not user.is_active:
        await websocket.close(code=1008)
        return

    user_id = str(user.id)
    await manager.connect(user_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id, websocket)