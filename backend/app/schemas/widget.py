"""Widget schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class WidgetBase(BaseModel):
    widget_type: str
    config: dict[str, Any] = Field(default_factory=dict)
    position_x: int = Field(default=0, ge=0)
    position_y: int = Field(default=0, ge=0)
    width: int = Field(default=2, gt=0)
    height: int = Field(default=2, gt=0)


class WidgetCreate(WidgetBase):
    pass


class WidgetUpdate(BaseModel):
    config: dict[str, Any] | None = None
    position_x: int | None = Field(default=None, ge=0)
    position_y: int | None = Field(default=None, ge=0)
    width: int | None = Field(default=None, gt=0)
    height: int | None = Field(default=None, gt=0)


class WidgetRead(ORMModel):
    id: int
    layout_id: int
    widget_type: str
    config: dict[str, Any]
    position_x: int
    position_y: int
    width: int
    height: int
    created_at: datetime
    updated_at: datetime
