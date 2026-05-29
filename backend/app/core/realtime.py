"""Realtime layer: Redis pub/sub fan-out + WebSocket connection manager.

Displays open a WebSocket to receive layout/status changes in realtime. When a
layout is updated or a display is reassigned, the API publishes an event to
Redis; every API instance subscribed to the channel pushes it to the relevant
connected sockets. This scales horizontally across multiple backend replicas.

If Redis is unavailable the manager degrades gracefully to in-process delivery
so local development without Redis still works.
"""
from __future__ import annotations

import asyncio
import json
import logging
from collections import defaultdict
from typing import Any

import redis.asyncio as aioredis
from fastapi import WebSocket

from app.core.config import settings

logger = logging.getLogger("tokencast.realtime")

CHANNEL = "tokencast:events"


class ConnectionManager:
    def __init__(self) -> None:
        # display_id -> set of sockets currently rendering that display
        self._display_sockets: dict[int, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()
        self._redis: aioredis.Redis | None = None
        self._pubsub_task: asyncio.Task | None = None

    async def startup(self) -> None:
        try:
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            await self._redis.ping()
            self._pubsub_task = asyncio.create_task(self._listen())
            logger.info("Realtime: connected to Redis at %s", settings.REDIS_URL)
        except Exception as exc:  # pragma: no cover - depends on environment
            logger.warning("Realtime: Redis unavailable (%s); using in-process delivery", exc)
            self._redis = None

    async def shutdown(self) -> None:
        if self._pubsub_task:
            self._pubsub_task.cancel()
        if self._redis:
            await self._redis.aclose()

    async def connect(self, display_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._display_sockets[display_id].add(websocket)

    async def disconnect(self, display_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            self._display_sockets[display_id].discard(websocket)
            if not self._display_sockets[display_id]:
                self._display_sockets.pop(display_id, None)

    async def publish(self, event: str, display_id: int, payload: dict[str, Any] | None = None) -> None:
        message = {"event": event, "display_id": display_id, "payload": payload or {}}
        if self._redis:
            await self._redis.publish(CHANNEL, json.dumps(message))
        else:
            await self._deliver(message)

    async def _listen(self) -> None:  # pragma: no cover - long-running task
        assert self._redis is not None
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(CHANNEL)
        async for raw in pubsub.listen():
            if raw.get("type") != "message":
                continue
            try:
                message = json.loads(raw["data"])
            except (ValueError, KeyError):
                continue
            await self._deliver(message)

    async def _deliver(self, message: dict[str, Any]) -> None:
        display_id = message.get("display_id")
        sockets = list(self._display_sockets.get(display_id, set()))
        dead: list[WebSocket] = []
        for ws in sockets:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(display_id, ws)


manager = ConnectionManager()
