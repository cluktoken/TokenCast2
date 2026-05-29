"""User schemas."""
from __future__ import annotations

from datetime import datetime

from pydantic import EmailStr, Field

from app.schemas.common import ORMModel


class UserRead(ORMModel):
    id: int
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_superuser: bool
    auth_provider: str
    created_at: datetime


class UserUpdate(ORMModel):
    full_name: str | None = Field(default=None, max_length=255)
