"""Layout schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.widget import WidgetCreate, WidgetRead


class LayoutBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    theme: str = Field(default="dark", max_length=64)
    grid_config: dict[str, Any] = Field(
        default_factory=lambda: {"columns": 12, "rows": 8, "gap": 8}
    )


class LayoutCreate(LayoutBase):
    # Optionally seed widgets at creation time (used by the AI builder).
    widgets: list[WidgetCreate] = Field(default_factory=list)


class LayoutUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    theme: str | None = Field(default=None, max_length=64)
    grid_config: dict[str, Any] | None = None


class LayoutRead(ORMModel):
    id: int
    user_id: int
    name: str
    theme: str
    grid_config: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class LayoutDetail(LayoutRead):
    widgets: list[WidgetRead] = Field(default_factory=list)
