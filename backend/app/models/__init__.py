"""ORM models package.

Importing this package registers every model on the shared declarative Base,
which is what Alembic's autogenerate and Base.metadata.create_all rely on.
"""
from app.core.database import Base
from app.models.display import Display, DeviceType, DisplayStatus
from app.models.layout import Layout
from app.models.template import Template
from app.models.user import User
from app.models.widget import Widget

__all__ = [
    "Base",
    "User",
    "Display",
    "DeviceType",
    "DisplayStatus",
    "Layout",
    "Widget",
    "Template",
]
