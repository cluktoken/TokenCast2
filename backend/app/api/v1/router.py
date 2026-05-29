"""Aggregate router for API v1."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import ai, auth, displays, layouts, templates, widgets, ws

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(displays.router)
api_router.include_router(layouts.router)
api_router.include_router(widgets.router)
api_router.include_router(templates.router)
api_router.include_router(ai.router)

# WebSocket routes are mounted at the app root (no /api/v1 prefix) in main.py.
ws_router = ws.router
