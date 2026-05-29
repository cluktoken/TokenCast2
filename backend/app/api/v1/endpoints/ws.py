"""WebSocket endpoint for realtime display/player updates."""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.realtime import manager

router = APIRouter()


@router.websocket("/ws/displays/{display_id}")
async def display_socket(websocket: WebSocket, display_id: int) -> None:
    """A player connects here to receive layout/status events for its display.

    Auth note: the player authenticates via a query token in production; for the
    foundation the socket is scoped to a single display id and only receives
    that display's events.
    """
    await manager.connect(display_id, websocket)
    try:
        await websocket.send_json({"event": "connected", "display_id": display_id})
        while True:
            # We don't require inbound messages, but reading keeps the socket
            # alive and lets clients send ping frames.
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(display_id, websocket)
    except Exception:
        await manager.disconnect(display_id, websocket)
