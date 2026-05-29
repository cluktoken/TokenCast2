"""Template, AI builder and dashboard schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class TemplateRead(ORMModel):
    id: int
    user_id: int | None
    name: str
    description: str | None
    category: str
    is_system: bool
    definition: dict[str, Any]
    created_at: datetime


class TemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category: str = "general"
    # If omitted, the template is built from an existing layout id.
    definition: dict[str, Any] | None = None
    from_layout_id: int | None = None


class InstantiateTemplateRequest(BaseModel):
    name: str | None = Field(default=None, max_length=255)


class AIBuildRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)
    theme: str | None = None
    # When true, persist the generated layout immediately and return it.
    save: bool = True


class AIBuildResponse(BaseModel):
    name: str
    theme: str
    grid_config: dict[str, Any]
    widgets: list[dict[str, Any]]
    layout_id: int | None = None
    source: str  # "llm" or "builtin"


class DashboardStats(BaseModel):
    total_displays: int
    online_displays: int
    total_layouts: int
    widget_count: int
    recent_activity: list[dict[str, Any]]
