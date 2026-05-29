"""Authentication / account service."""
from __future__ import annotations

from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import (
    TokenType,
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.exceptions import AuthError, ConflictError, NotFoundError
from app.models.user import User
from app.repositories import UserRepository
from app.schemas.auth import RegisterRequest, TokenPair


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, data: RegisterRequest) -> User:
        if self.users.get_by_email(data.email):
            raise ConflictError("An account with that email already exists.")
        user = User(
            email=data.email.lower(),
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
        )
        return self.users.add(user)

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthError("Incorrect email or password.")
        if not user.is_active:
            raise AuthError("Account is disabled.")
        return user

    def issue_tokens(self, user: User) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token, TokenType.REFRESH)
        except JWTError:
            raise AuthError("Invalid or expired refresh token.")
        user = self.users.get(int(payload["sub"]))
        if not user or not user.is_active:
            raise AuthError("User no longer exists.")
        return self.issue_tokens(user)

    def begin_password_reset(self, email: str) -> str | None:
        """Return a reset token if the account exists, else None.

        The endpoint always responds identically to avoid leaking which emails
        are registered.
        """
        user = self.users.get_by_email(email)
        if not user:
            return None
        return create_password_reset_token(user.id)

    def confirm_password_reset(self, token: str, new_password: str) -> None:
        try:
            payload = decode_token(token, TokenType.PASSWORD_RESET)
        except JWTError:
            raise AuthError("Invalid or expired reset token.")
        user = self.users.get(int(payload["sub"]))
        if not user:
            raise NotFoundError("User not found.")
        user.hashed_password = hash_password(new_password)
        self.users.save(user)

    def current_user_from_token(self, token: str) -> User:
        try:
            payload = decode_token(token, TokenType.ACCESS)
        except JWTError:
            raise AuthError("Could not validate credentials.")
        user = self.users.get(int(payload["sub"]))
        if not user or not user.is_active:
            raise AuthError("Could not validate credentials.")
        return user
