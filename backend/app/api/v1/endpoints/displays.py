"""Display endpoints."""
from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.core.realtime import manager
from app.schemas.common import Message
from app.schemas.display import (
    AssignLayoutRequest,
    DisplayCreate,
    DisplayPlayerView,
    DisplayRead,
    DisplayUpdate,
)
from app.schemas.layout import LayoutDetail
from app.services.display import DisplayService
from app.services.layout import LayoutService

router = APIRouter(prefix="/displays", tags=["displays"])


@router.get("", response_model=list[DisplayRead])
def list_displays(user: CurrentUser, db: DbSession) -> list[DisplayRead]:
    return [DisplayRead.model_validate(d) for d in DisplayService(db).list(user.id)]


@router.post("", response_model=DisplayRead, status_code=201)
def create_display(data: DisplayCreate, user: CurrentUser, db: DbSession) -> DisplayRead:
    return DisplayRead.model_validate(DisplayService(db).create(user.id, data))


@router.get("/{display_id}", response_model=DisplayRead)
def get_display(display_id: int, user: CurrentUser, db: DbSession) -> DisplayRead:
    return DisplayRead.model_validate(DisplayService(db).get(display_id, user.id))


@router.patch("/{display_id}", response_model=DisplayRead)
def update_display(
    display_id: int, data: DisplayUpdate, user: CurrentUser, db: DbSession
) -> DisplayRead:
    return DisplayRead.model_validate(DisplayService(db).update(display_id, user.id, data))


@router.delete("/{display_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_display(display_id: int, user: CurrentUser, db: DbSession) -> None:
    DisplayService(db).delete(display_id, user.id)


@router.post("/{display_id}/assign", response_model=DisplayRead)
async def assign_layout(
    display_id: int, data: AssignLayoutRequest, user: CurrentUser, db: DbSession
) -> DisplayRead:
    display = DisplayService(db).assign_layout(display_id, user.id, data.layout_id)
    db.commit()
    # Tell any connected player to reload its layout immediately.
    await manager.publish("layout_assigned", display_id, {"layout_id": data.layout_id})
    return DisplayRead.model_validate(display)


@router.get("/{display_id}/player", response_model=DisplayPlayerView)
def player_view(display_id: int, user: CurrentUser, db: DbSession) -> DisplayPlayerView:
    """Full payload the fullscreen player renders: display + resolved layout."""
    display = DisplayService(db).get(display_id, user.id)
    layout_detail = None
    if display.current_layout_id:
        layout = LayoutService(db).get(display.current_layout_id, user.id)
        layout_detail = LayoutDetail.model_validate(layout)
    return DisplayPlayerView(
        display=DisplayRead.model_validate(display), layout=layout_detail
    )


@router.post("/{display_id}/heartbeat", response_model=Message)
async def heartbeat(display_id: int, user: CurrentUser, db: DbSession) -> Message:
    DisplayService(db).get(display_id, user.id)  # ownership check
    DisplayService(db).heartbeat(display_id)
    db.commit()
    await manager.publish("heartbeat", display_id, {"status": "online"})
    return Message(detail="ok")
