"""Widget entity -- the heart of the system. Everything is a widget."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.json_type import JSONType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.layout import Layout


class Widget(Base, TimestampMixin):
    __tablename__ = "widgets"
    __table_args__ = (
        CheckConstraint("width > 0", name="ck_widget_width_positive"),
        CheckConstraint("height > 0", name="ck_widget_height_positive"),
        CheckConstraint("position_x >= 0", name="ck_widget_x_nonneg"),
        CheckConstraint("position_y >= 0", name="ck_widget_y_nonneg"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    layout_id: Mapped[int] = mapped_column(
        ForeignKey("layouts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    # `widget_type` is a registry key (see app.widgets.registry), not an enum,
    # so new widget plugins can be added without a schema migration.
    widget_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    config: Mapped[dict[str, Any]] = mapped_column(
        JSONType, default=dict, nullable=False
    )

    position_x: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    position_y: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    width: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    height: Mapped[int] = mapped_column(Integer, default=2, nullable=False)

    layout: Mapped["Layout"] = relationship(back_populates="widgets")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Widget id={self.id} type={self.widget_type!r} layout={self.layout_id}>"
