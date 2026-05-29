"""Template endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.layout import LayoutDetail
from app.schemas.template import (
    InstantiateTemplateRequest,
    TemplateCreate,
    TemplateRead,
)
from app.services.template import TemplateService

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=list[TemplateRead])
def list_templates(user: CurrentUser, db: DbSession) -> list[TemplateRead]:
    return [TemplateRead.model_validate(t) for t in TemplateService(db).list(user.id)]


@router.get("/{template_id}", response_model=TemplateRead)
def get_template(template_id: int, user: CurrentUser, db: DbSession) -> TemplateRead:
    return TemplateRead.model_validate(TemplateService(db).get(template_id, user.id))


@router.post("", response_model=TemplateRead, status_code=201)
def create_template(data: TemplateCreate, user: CurrentUser, db: DbSession) -> TemplateRead:
    return TemplateRead.model_validate(TemplateService(db).create(user.id, data))


@router.post("/{template_id}/instantiate", response_model=LayoutDetail, status_code=201)
def instantiate_template(
    template_id: int, data: InstantiateTemplateRequest, user: CurrentUser, db: DbSession
) -> LayoutDetail:
    layout = TemplateService(db).instantiate(template_id, user.id, data.name)
    return LayoutDetail.model_validate(layout)
