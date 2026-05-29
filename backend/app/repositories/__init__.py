"""Concrete repositories for each entity."""
from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.display import Display, DisplayStatus
from app.models.layout import Layout
from app.models.template import Template
from app.models.user import User
from app.models.widget import Widget
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email.lower()))


class DisplayRepository(BaseRepository[Display]):
    model = Display

    def list_for_user(self, user_id: int) -> list[Display]:
        stmt = select(Display).where(Display.user_id == user_id).order_by(Display.created_at)
        return list(self.db.scalars(stmt).all())

    def get_owned(self, display_id: int, user_id: int) -> Display | None:
        return self.db.scalar(
            select(Display).where(Display.id == display_id, Display.user_id == user_id)
        )

    def get_by_pairing_code(self, code: str) -> Display | None:
        return self.db.scalar(select(Display).where(Display.pairing_code == code))

    def count_for_user(self, user_id: int) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Display).where(Display.user_id == user_id)
        ) or 0

    def count_online_for_user(self, user_id: int) -> int:
        return self.db.scalar(
            select(func.count())
            .select_from(Display)
            .where(Display.user_id == user_id, Display.status == DisplayStatus.ONLINE)
        ) or 0


class LayoutRepository(BaseRepository[Layout]):
    model = Layout

    def list_for_user(self, user_id: int) -> list[Layout]:
        stmt = (
            select(Layout)
            .where(Layout.user_id == user_id)
            .options(selectinload(Layout.widgets))
            .order_by(Layout.created_at)
        )
        return list(self.db.scalars(stmt).all())

    def get_owned(self, layout_id: int, user_id: int) -> Layout | None:
        return self.db.scalar(
            select(Layout)
            .where(Layout.id == layout_id, Layout.user_id == user_id)
            .options(selectinload(Layout.widgets))
        )

    def get_with_widgets(self, layout_id: int) -> Layout | None:
        return self.db.scalar(
            select(Layout)
            .where(Layout.id == layout_id)
            .options(selectinload(Layout.widgets))
        )

    def count_for_user(self, user_id: int) -> int:
        return self.db.scalar(
            select(func.count()).select_from(Layout).where(Layout.user_id == user_id)
        ) or 0


class WidgetRepository(BaseRepository[Widget]):
    model = Widget

    def list_for_layout(self, layout_id: int) -> list[Widget]:
        return list(
            self.db.scalars(
                select(Widget).where(Widget.layout_id == layout_id).order_by(Widget.id)
            ).all()
        )

    def count_for_user(self, user_id: int) -> int:
        return self.db.scalar(
            select(func.count())
            .select_from(Widget)
            .join(Layout, Widget.layout_id == Layout.id)
            .where(Layout.user_id == user_id)
        ) or 0


class TemplateRepository(BaseRepository[Template]):
    model = Template

    def list_visible(self, user_id: int) -> list[Template]:
        """System templates plus the user's own templates."""
        stmt = (
            select(Template)
            .where(or_(Template.is_system.is_(True), Template.user_id == user_id))
            .order_by(Template.is_system.desc(), Template.created_at)
        )
        return list(self.db.scalars(stmt).all())

    def get_visible(self, template_id: int, user_id: int) -> Template | None:
        return self.db.scalar(
            select(Template).where(
                Template.id == template_id,
                or_(Template.is_system.is_(True), Template.user_id == user_id),
            )
        )
