"""TokenCast 2.0 application entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.v1.router import api_router, ws_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.exceptions import DomainError
from app.core.realtime import manager
from app.core.seed import seed_system_templates

# Importing the models package registers every model on Base.metadata.
import app.models  # noqa: F401  (side-effect import)
# Importing the widgets package registers every widget plugin.
import app.widgets  # noqa: F401  (side-effect import)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tokencast")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # In production, schema is managed by Alembic. For local/dev convenience we
    # ensure tables exist and seed system templates.
    if not settings.is_production:
        Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        try:
            seed_system_templates(db)
        except Exception as exc:  # don't let seeding crash startup
            logger.warning("Seeding skipped: %s", exc)
    await manager.startup()
    logger.info("TokenCast %s started (env=%s)", __version__, settings.ENVIRONMENT)
    yield
    await manager.shutdown()


app = FastAPI(
    title=f"{settings.PROJECT_NAME} API",
    version=__version__,
    description="AI-powered programmable display platform.",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/", tags=["meta"])
async def root() -> dict[str, str]:
    return {"name": settings.PROJECT_NAME, "version": __version__, "status": "online"}


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


# REST API (versioned) + WebSocket routes (root-mounted).
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
app.include_router(ws_router)
