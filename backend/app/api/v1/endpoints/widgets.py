"""Widget catalog endpoint -- drives the layout builder palette and AI builder."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.widgets import registry

router = APIRouter(prefix="/widgets", tags=["widgets"])


@router.get("/catalog")
def widget_catalog() -> dict[str, list[dict[str, Any]]]:
    """Every registered widget type with its config schema and defaults."""
    return {"widgets": registry.catalog()}
