"""Display service -- device lifecycle, pairing, assignment, heartbeat."""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.display import Display, DisplayStatus
from app.repositories import DisplayRepository, LayoutRepository
from app.schemas.display import DisplayCreate, DisplayUpdate


class DisplayService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.displays = DisplayRepository(db)
        self.layouts = LayoutRepository(db)

    def list(self, user_id: int) -> list[Display]:
        return self.displays.list_for_user(user_id)

    def get(self, display_id: int, user_id: int) -> Display:
        display = self.displays.get_owned(display_id, user_id)
        if not display:
            raise NotFoundError("Display not found.")
        return display

    def create(self, user_id: int, data: DisplayCreate) -> Display:
        display = Display(
            user_id=user_id,
            name=data.name,
            device_type=data.device_type,
            group=data.group,
            status=DisplayStatus.UNPAIRED,
            pairing_code=self._new_pairing_code(),
        )
        return self.displays.add(display)

    def update(self, display_id: int, user_id: int, data: DisplayUpdate) -> Display:
        display = self.get(display_id, user_id)
        if data.name is not None:
            display.name = data.name
        if data.device_type is not None:
            display.device_type = data.device_type
        if data.group is not None:
            display.group = data.group
        if data.current_layout_id is not None:
            self._validate_layout(data.current_layout_id, user_id)
            display.current_layout_id = data.current_layout_id
        return self.displays.save(display)

    def delete(self, display_id: int, user_id: int) -> None:
        display = self.get(display_id, user_id)
        self.displays.delete(display)

    def assign_layout(self, display_id: int, user_id: int, layout_id: int | None) -> Display:
        display = self.get(display_id, user_id)
        if layout_id is not None:
            self._validate_layout(layout_id, user_id)
        display.current_layout_id = layout_id
        return self.displays.save(display)

    def heartbeat(self, display_id: int) -> Display:
        """Mark a display online; called by the device player periodically."""
        display = self.displays.get(display_id)
        if not display:
            raise NotFoundError("Display not found.")
        display.status = DisplayStatus.ONLINE
        display.last_seen = datetime.now(timezone.utc)
        return self.displays.save(display)

    def _validate_layout(self, layout_id: int, user_id: int) -> None:
        if not self.layouts.get_owned(layout_id, user_id):
            raise NotFoundError("Layout not found.")

    @staticmethod
    def _new_pairing_code() -> str:
        return secrets.token_hex(3).upper()  # 6 hex chars, e.g. "A1B2C3"
