"""Layout entity -- a themed grid that contains Widgets."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.json_type import JSONType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.widget import Widget


DEFAULT_GRID_CONFIG: dict[str, Any] = {"columns": 12, "rows": 8, "gap": 8}


class Layout(Base, TimestampMixin):
    __tablename__ = "layouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    theme: Mapped[str] = mapped_column(String(64), default="dark", nullable=False)
    grid_config: Mapped[dict[str, Any]] = mapped_column(
        JSONType, default=lambda: dict(DEFAULT_GRID_CONFIG), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="layouts")
    widgets: Mapped[list["Widget"]] = relationship(
        back_populates="layout",
        cascade="all, delete-orphan",
        order_by="Widget.id",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Layout id={self.id} name={self.name!r} theme={self.theme}>"
