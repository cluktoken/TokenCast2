"""Layout service -- create, update, clone layouts and seed widgets."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.layout import Layout
from app.models.widget import Widget
from app.repositories import LayoutRepository
from app.schemas.layout import LayoutCreate, LayoutUpdate
from app.widgets import registry


class LayoutService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.layouts = LayoutRepository(db)

    def list(self, user_id: int) -> list[Layout]:
        return self.layouts.list_for_user(user_id)

    def get(self, layout_id: int, user_id: int) -> Layout:
        layout = self.layouts.get_owned(layout_id, user_id)
        if not layout:
            raise NotFoundError("Layout not found.")
        return layout

    def create(self, user_id: int, data: LayoutCreate) -> Layout:
        layout = Layout(
            user_id=user_id,
            name=data.name,
            theme=data.theme,
            grid_config=data.grid_config,
        )
        for w in data.widgets:
            if not registry.has(w.widget_type):
                continue  # silently skip unknown types from AI/template input
            definition = registry.get(w.widget_type)
            layout.widgets.append(
                Widget(
                    widget_type=w.widget_type,
                    config=definition.validate_config(w.config),
                    position_x=w.position_x,
                    position_y=w.position_y,
                    width=max(w.width, definition.min_width),
                    height=max(w.height, definition.min_height),
                )
            )
        return self.layouts.add(layout)

    def update(self, layout_id: int, user_id: int, data: LayoutUpdate) -> Layout:
        layout = self.get(layout_id, user_id)
        if data.name is not None:
            layout.name = data.name
        if data.theme is not None:
            layout.theme = data.theme
        if data.grid_config is not None:
            layout.grid_config = data.grid_config
        return self.layouts.save(layout)

    def delete(self, layout_id: int, user_id: int) -> None:
        layout = self.get(layout_id, user_id)
        self.layouts.delete(layout)

    def clone(self, layout_id: int, user_id: int) -> Layout:
        original = self.get(layout_id, user_id)
        clone = Layout(
            user_id=user_id,
            name=f"{original.name} (copy)",
            theme=original.theme,
            grid_config=dict(original.grid_config),
        )
        for w in original.widgets:
            clone.widgets.append(
                Widget(
                    widget_type=w.widget_type,
                    config=dict(w.config),
                    position_x=w.position_x,
                    position_y=w.position_y,
                    width=w.width,
                    height=w.height,
                )
            )
        return self.layouts.add(clone)
