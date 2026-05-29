"""Display entity -- any screen that renders a Layout."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.layout import Layout
    from app.models.user import User


class DeviceType(str, Enum):
    BROWSER = "browser"
    WINDOWS = "windows"
    LINUX = "linux"
    RASPBERRY_PI = "raspberry_pi"
    ANDROID_TV = "android_tv"
    FIRE_TV = "fire_tv"
    SAMSUNG_TV = "samsung_tv"
    LG_TV = "lg_tv"
    TABLET = "tablet"
    OTHER = "other"


class DisplayStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    UNPAIRED = "unpaired"


class Display(Base, TimestampMixin):
    __tablename__ = "displays"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(
        SAEnum(DeviceType, name="device_type"), default=DeviceType.BROWSER, nullable=False
    )
    status: Mapped[DisplayStatus] = mapped_column(
        SAEnum(DisplayStatus, name="display_status"),
        default=DisplayStatus.UNPAIRED,
        nullable=False,
    )
    # Short code used by a device to pair itself to this display record.
    pairing_code: Mapped[str | None] = mapped_column(String(12), index=True)
    group: Mapped[str | None] = mapped_column(String(120), index=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    current_layout_id: Mapped[int | None] = mapped_column(
        ForeignKey("layouts.id", ondelete="SET NULL"), index=True
    )

    user: Mapped["User"] = relationship(back_populates="displays")
    current_layout: Mapped["Layout | None"] = relationship(
        "Layout", foreign_keys=[current_layout_id]
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Display id={self.id} name={self.name!r} status={self.status}>"
