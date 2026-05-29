"""Widget service -- owns config validation through the plugin registry."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, PermissionError_
from app.models.widget import Widget
from app.repositories import LayoutRepository, WidgetRepository
from app.schemas.widget import WidgetCreate, WidgetUpdate
from app.widgets import registry


class WidgetService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.widgets = WidgetRepository(db)
        self.layouts = LayoutRepository(db)

    def _ensure_layout_owned(self, layout_id: int, user_id: int) -> None:
        if not self.layouts.get_owned(layout_id, user_id):
            raise NotFoundError("Layout not found.")

    def create(self, layout_id: int, user_id: int, data: WidgetCreate) -> Widget:
        self._ensure_layout_owned(layout_id, user_id)
        if not registry.has(data.widget_type):
            raise NotFoundError(f"Unknown widget type: {data.widget_type}")
        definition = registry.get(data.widget_type)
        clean_config = definition.validate_config(data.config)
        widget = Widget(
            layout_id=layout_id,
            widget_type=data.widget_type,
            config=clean_config,
            position_x=data.position_x,
            position_y=data.position_y,
            width=max(data.width, definition.min_width),
            height=max(data.height, definition.min_height),
        )
        return self.widgets.add(widget)

    def _get_owned(self, widget_id: int, user_id: int) -> Widget:
        widget = self.widgets.get(widget_id)
        if not widget:
            raise NotFoundError("Widget not found.")
        layout = self.layouts.get(widget.layout_id)
        if not layout or layout.user_id != user_id:
            raise PermissionError_("You do not own this widget.")
        return widget

    def update(self, widget_id: int, user_id: int, data: WidgetUpdate) -> Widget:
        widget = self._get_owned(widget_id, user_id)
        if data.config is not None:
            definition = registry.get(widget.widget_type)
            widget.config = definition.validate_config(data.config)
        for field in ("position_x", "position_y", "width", "height"):
            value = getattr(data, field)
            if value is not None:
                setattr(widget, field, value)
        return self.widgets.save(widget)

    def delete(self, widget_id: int, user_id: int) -> None:
        widget = self._get_owned(widget_id, user_id)
        self.widgets.delete(widget)
