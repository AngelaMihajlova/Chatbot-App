import asyncio
from typing import Dict, Optional, Set

from fastapi import WebSocket


class ConnectionManager:
    """Tracks live WebSocket connections per user for pushing account-level updates."""

    def __init__(self) -> None:
        self._connections: Dict[str, Set[WebSocket]] = {}
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(user_id, set()).add(websocket)

    def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        conns = self._connections.get(user_id)
        if not conns:
            return
        conns.discard(websocket)
        if not conns:
            self._connections.pop(user_id, None)

    async def _broadcast(self, user_id: str, message: dict) -> None:
        for ws in list(self._connections.get(user_id, ())):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(user_id, ws)

    def notify(self, user_id: str, message: dict) -> None:
        """Schedule a push to a user's active sockets. Safe to call from sync request handlers."""
        if self._loop is None or not self._connections.get(user_id):
            return
        asyncio.run_coroutine_threadsafe(self._broadcast(user_id, message), self._loop)


manager = ConnectionManager()