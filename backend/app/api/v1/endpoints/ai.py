"""AI builder and dashboard endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.layout import LayoutCreate, WidgetCreate
from app.schemas.template import AIBuildRequest, AIBuildResponse, DashboardStats
from app.services.ai_builder import AIBuilderService
from app.services.layout import LayoutService
from app.services.template import DashboardService

router = APIRouter(tags=["ai", "dashboard"])


@router.post("/ai/build", response_model=AIBuildResponse)
def ai_build(data: AIBuildRequest, user: CurrentUser, db: DbSession) -> AIBuildResponse:
    plan = AIBuilderService().build(data.prompt, data.theme)
    layout_id = None
    if data.save:
        layout_in = LayoutCreate(
            name=plan["name"],
            theme=plan["theme"],
            grid_config=plan["grid_config"],
            widgets=[WidgetCreate(**w) for w in plan["widgets"]],
        )
        layout = LayoutService(db).create(user.id, layout_in)
        layout_id = layout.id
    return AIBuildResponse(
        name=plan["name"],
        theme=plan["theme"],
        grid_config=plan["grid_config"],
        widgets=plan["widgets"],
        layout_id=layout_id,
        source=plan["source"],
    )


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(user: CurrentUser, db: DbSession) -> DashboardStats:
    return DashboardService(db).stats(user.id)
