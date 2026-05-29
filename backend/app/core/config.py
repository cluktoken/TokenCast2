"""Application configuration.

All runtime configuration is read from environment variables (or a local .env
file) via pydantic-settings. Nothing else in the codebase should read os.environ
directly -- everything goes through the singleton `settings` object below.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Core ---
    PROJECT_NAME: str = "TokenCast"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # --- Security / Auth ---
    SECRET_KEY: str = "change-me-in-production-please-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Database ---
    # Synchronous URL used by Alembic + the default SQLAlchemy engine.
    DATABASE_URL: str = "postgresql+psycopg2://tokencast:tokencast@db:5432/tokencast"

    # --- Redis / realtime ---
    REDIS_URL: str = "redis://redis:6379/0"

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # --- AI builder (OpenAI-compatible) ---
    # Leave AI_API_KEY empty to use the built-in deterministic generator.
    AI_API_BASE: str = "https://api.openai.com/v1"
    AI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
