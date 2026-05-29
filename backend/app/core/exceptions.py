"""Domain exceptions raised by the service layer.

These are translated into HTTP responses by an exception handler in main.py,
so services never import FastAPI.
"""
from __future__ import annotations


class DomainError(Exception):
    status_code = 400

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class NotFoundError(DomainError):
    status_code = 404


class ConflictError(DomainError):
    status_code = 409


class AuthError(DomainError):
    status_code = 401


class PermissionError_(DomainError):
    status_code = 403
