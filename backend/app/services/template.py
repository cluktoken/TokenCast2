"""Template service + dashboard statistics."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.display import Display
from app.models.layout import Layout
from app.models.template import Template
from app.repositories import (
    DisplayRepository,
    LayoutRepository,
    TemplateRepository,
    WidgetRepository,
)
from app.schemas.layout import LayoutCreate, WidgetCreate
from app.schemas.template import DashboardStats, TemplateCreate
from app.services.layout import LayoutService


class TemplateService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.templates = TemplateRepository(db)
        self.layouts = LayoutRepository(db)
        self.layout_service = LayoutService(db)

    def list(self, user_id: int) -> list[Template]:
        return self.templates.list_visible(user_id)

    def get(self, template_id: int, user_id: int) -> Template:
        template = self.templates.get_visible(template_id, user_id)
        if not template:
            raise NotFoundError("Template not found.")
        return template

    def create(self, user_id: int, data: TemplateCreate) -> Template:
        definition = data.definition
        if definition is None and data.from_layout_id is not None:
            layout = self.layouts.get_owned(data.from_layout_id, user_id)
            if not layout:
                raise NotFoundError("Source layout not found.")
            definition = self._serialize_layout(layout)
        if definition is None:
            definition = {"theme": "dark", "grid_config": {"columns": 12, "rows": 8, "gap": 8}, "widgets": []}
        template = Template(
            user_id=user_id,
            name=data.name,
            description=data.description,
            category=data.category,
            is_system=False,
            definition=definition,
        )
        self.db.add(template)
        self.db.flush()
        self.db.refresh(template)
        return template

    def instantiate(self, template_id: int, user_id: int, name: str | None) -> Layout:
        template = self.get(template_id, user_id)
        definition = template.definition
        widgets = [WidgetCreate(**w) for w in definition.get("widgets", [])]
        layout_in = LayoutCreate(
            name=name or template.name,
            theme=definition.get("theme", "dark"),
            grid_config=definition.get("grid_config", {"columns": 12, "rows": 8, "gap": 8}),
            widgets=widgets,
        )
        return self.layout_service.create(user_id, layout_in)

    @staticmethod
    def _serialize_layout(layout: Layout) -> dict[str, Any]:
        return {
            "theme": layout.theme,
            "grid_config": layout.grid_config,
            "widgets": [
                {
                    "widget_type": w.widget_type,
                    "config": w.config,
                    "position_x": w.position_x,
                    "position_y": w.position_y,
                    "width": w.width,
                    "height": w.height,
                }
                for w in layout.widgets
            ],
        }


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.displays = DisplayRepository(db)
        self.layouts = LayoutRepository(db)
        self.widgets = WidgetRepository(db)

    def stats(self, user_id: int) -> DashboardStats:
        return DashboardStats(
            total_displays=self.displays.count_for_user(user_id),
            online_displays=self.displays.count_online_for_user(user_id),
            total_layouts=self.layouts.count_for_user(user_id),
            widget_count=self.widgets.count_for_user(user_id),
            recent_activity=self._recent_activity(user_id),
        )

    def _recent_activity(self, user_id: int, limit: int = 8) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        displays = self.db.scalars(
            select(Display)
            .where(Display.user_id == user_id)
            .order_by(Display.updated_at.desc())
            .limit(limit)
        ).all()
        for d in displays:
            events.append({
                "type": "display",
                "id": d.id,
                "name": d.name,
                "status": d.status.value,
                "at": _iso(d.updated_at),
            })
        layouts = self.db.scalars(
            select(Layout)
            .where(Layout.user_id == user_id)
            .order_by(Layout.updated_at.desc())
            .limit(limit)
        ).all()
        for layout in layouts:
            events.append({
                "type": "layout",
                "id": layout.id,
                "name": layout.name,
                "at": _iso(layout.updated_at),
            })
        events.sort(key=lambda e: e["at"] or "", reverse=True)
        return events[:limit]


def _iso(dt: datetime | None) -> str | None:
    return dt.isoformat() if dt else None
