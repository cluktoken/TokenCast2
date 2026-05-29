"""Display schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models.display import DeviceType, DisplayStatus
from app.schemas.common import ORMModel
from app.schemas.layout import LayoutDetail


class DisplayBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    device_type: DeviceType = DeviceType.BROWSER
    group: str | None = Field(default=None, max_length=120)


class DisplayCreate(DisplayBase):
    pass


class DisplayUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    device_type: DeviceType | None = None
    group: str | None = Field(default=None, max_length=120)
    current_layout_id: int | None = None


class AssignLayoutRequest(BaseModel):
    layout_id: int | None = None


class DisplayRead(ORMModel):
    id: int
    user_id: int
    name: str
    device_type: DeviceType
    status: DisplayStatus
    group: str | None
    pairing_code: str | None
    last_seen: datetime | None
    current_layout_id: int | None
    created_at: datetime
    updated_at: datetime


class DisplayPlayerView(BaseModel):
    """Payload consumed by the fullscreen player on a device."""

    display: DisplayRead
    layout: LayoutDetail | None
