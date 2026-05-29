"""Template entity -- a reusable, serialized layout blueprint.

A template stores a full layout definition (theme + grid + widgets) as JSON so
it can be instantiated into a real Layout for any user. System templates have a
NULL user_id and are visible to everyone.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.json_type import JSONType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class Template(Base, TimestampMixin):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(64), default="general", nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # { "theme": str, "grid_config": {...}, "widgets": [ {...}, ... ] }
    definition: Mapped[dict[str, Any]] = mapped_column(JSONType, nullable=False)

    user: Mapped["User | None"] = relationship(back_populates="templates")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Template id={self.id} name={self.name!r} system={self.is_system}>"
