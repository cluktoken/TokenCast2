"""Authentication endpoints."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUser, DbSession
from app.core.config import settings
from app.schemas.auth import (
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
)
from app.schemas.common import Message
from app.schemas.user import UserRead
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair, status_code=201)
def register(data: RegisterRequest, db: DbSession) -> TokenPair:
    service = AuthService(db)
    user = service.register(data)
    return service.issue_tokens(user)


@router.post("/login", response_model=TokenPair)
def login_form(
    db: DbSession,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenPair:
    """OAuth2 password flow (used by Swagger UI). username == email."""
    service = AuthService(db)
    user = service.authenticate(form.username, form.password)
    return service.issue_tokens(user)


@router.post("/login/json", response_model=TokenPair)
def login_json(data: LoginRequest, db: DbSession) -> TokenPair:
    service = AuthService(db)
    user = service.authenticate(data.email, data.password)
    return service.issue_tokens(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshRequest, db: DbSession) -> TokenPair:
    return AuthService(db).refresh(data.refresh_token)


@router.post("/logout", response_model=Message)
def logout(_: CurrentUser) -> Message:
    # Stateless JWT: the client discards its tokens. Endpoint exists so clients
    # have a clear contract and so a future token-blocklist can hook in here.
    return Message(detail="Logged out.")


@router.post("/password-reset", response_model=PasswordResetResponse)
def password_reset(data: PasswordResetRequest, db: DbSession) -> PasswordResetResponse:
    token = AuthService(db).begin_password_reset(data.email)
    return PasswordResetResponse(
        detail="If that account exists, a reset link has been sent.",
        reset_token=None if settings.is_production else token,
    )


@router.post("/password-reset/confirm", response_model=Message)
def password_reset_confirm(data: PasswordResetConfirm, db: DbSession) -> Message:
    AuthService(db).confirm_password_reset(data.token, data.new_password)
    return Message(detail="Password updated.")


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> UserRead:
    return UserRead.model_validate(user)
