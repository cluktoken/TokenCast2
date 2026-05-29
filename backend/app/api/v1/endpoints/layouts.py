"""Layout and nested widget endpoints."""
from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import CurrentUser, DbSession
from app.core.realtime import manager
from app.schemas.layout import LayoutCreate, LayoutDetail, LayoutRead, LayoutUpdate
from app.schemas.widget import WidgetCreate, WidgetRead, WidgetUpdate
from app.services.layout import LayoutService
from app.services.widget import WidgetService

router = APIRouter(prefix="/layouts", tags=["layouts"])


@router.get("", response_model=list[LayoutRead])
def list_layouts(user: CurrentUser, db: DbSession) -> list[LayoutRead]:
    return [LayoutRead.model_validate(layout) for layout in LayoutService(db).list(user.id)]


@router.post("", response_model=LayoutDetail, status_code=201)
def create_layout(data: LayoutCreate, user: CurrentUser, db: DbSession) -> LayoutDetail:
    return LayoutDetail.model_validate(LayoutService(db).create(user.id, data))


@router.get("/{layout_id}", response_model=LayoutDetail)
def get_layout(layout_id: int, user: CurrentUser, db: DbSession) -> LayoutDetail:
    return LayoutDetail.model_validate(LayoutService(db).get(layout_id, user.id))


@router.patch("/{layout_id}", response_model=LayoutDetail)
def update_layout(
    layout_id: int, data: LayoutUpdate, user: CurrentUser, db: DbSession
) -> LayoutDetail:
    return LayoutDetail.model_validate(LayoutService(db).update(layout_id, user.id, data))


@router.delete("/{layout_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_layout(layout_id: int, user: CurrentUser, db: DbSession) -> None:
    LayoutService(db).delete(layout_id, user.id)


@router.post("/{layout_id}/clone", response_model=LayoutDetail, status_code=201)
def clone_layout(layout_id: int, user: CurrentUser, db: DbSession) -> LayoutDetail:
    return LayoutDetail.model_validate(LayoutService(db).clone(layout_id, user.id))


# --- Nested widgets ---------------------------------------------------------

@router.get("/{layout_id}/widgets", response_model=list[WidgetRead])
def list_widgets(layout_id: int, user: CurrentUser, db: DbSession) -> list[WidgetRead]:
    layout = LayoutService(db).get(layout_id, user.id)
    return [WidgetRead.model_validate(w) for w in layout.widgets]


@router.post("/{layout_id}/widgets", response_model=WidgetRead, status_code=201)
async def add_widget(
    layout_id: int, data: WidgetCreate, user: CurrentUser, db: DbSession
) -> WidgetRead:
    widget = WidgetService(db).create(layout_id, user.id, data)
    db.commit()
    await manager.publish("layout_updated", 0, {"layout_id": layout_id})
    return WidgetRead.model_validate(widget)


@router.patch("/{layout_id}/widgets/{widget_id}", response_model=WidgetRead)
async def update_widget(
    layout_id: int, widget_id: int, data: WidgetUpdate, user: CurrentUser, db: DbSession
) -> WidgetRead:
    widget = WidgetService(db).update(widget_id, user.id, data)
    db.commit()
    await manager.publish("layout_updated", 0, {"layout_id": layout_id})
    return WidgetRead.model_validate(widget)


@router.delete(
    "/{layout_id}/widgets/{widget_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_widget(
    layout_id: int, widget_id: int, user: CurrentUser, db: DbSession
) -> None:
    WidgetService(db).delete(widget_id, user.id)
    db.commit()
    await manager.publish("layout_updated", 0, {"layout_id": layout_id})
