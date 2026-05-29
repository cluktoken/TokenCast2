"""A portable JSON column type.

Uses native JSONB on PostgreSQL (indexable, efficient) and falls back to the
generic JSON type on other backends such as SQLite used in tests. Models can
therefore be imported and exercised without a Postgres instance.
"""
from __future__ import annotations

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import TypeDecorator


class JSONType(TypeDecorator):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())
