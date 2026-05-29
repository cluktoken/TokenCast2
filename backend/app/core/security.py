"""Security primitives: password hashing and JWT encode/decode."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"
    PASSWORD_RESET = "password_reset"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _create_token(subject: str | int, token_type: TokenType, expires_minutes: int,
                  extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type.value,
        "iat": now,
        "exp": now + timedelta(minutes=expires_minutes),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str | int) -> str:
    return _create_token(subject, TokenType.ACCESS, settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(subject: str | int) -> str:
    return _create_token(subject, TokenType.REFRESH, settings.REFRESH_TOKEN_EXPIRE_MINUTES)


def create_password_reset_token(subject: str | int) -> str:
    return _create_token(
        subject, TokenType.PASSWORD_RESET, settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )


def decode_token(token: str, expected_type: TokenType | None = None) -> dict[str, Any]:
    """Decode and validate a JWT. Raises JWTError on any problem."""
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if expected_type is not None and payload.get("type") != expected_type.value:
        raise JWTError(f"Expected token type {expected_type.value}")
    return payload
