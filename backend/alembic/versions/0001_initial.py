"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-29

Creates the four core entities (users, layouts, displays, widgets) plus
templates, with indexes, foreign keys, check constraints and the Postgres
enum/JSONB types used by the models.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

device_type = sa.Enum(
    "browser", "windows", "linux", "raspberry_pi", "android_tv", "fire_tv",
    "samsung_tv", "lg_tv", "tablet", "other", name="device_type",
)
display_status = sa.Enum("online", "offline", "unpaired", name="display_status")


def _json():
    return postgresql.JSONB(astext_type=sa.Text()).with_variant(sa.JSON(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("auth_provider", sa.String(32), nullable=False, server_default="local"),
        sa.Column("provider_subject", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "layouts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("theme", sa.String(64), nullable=False, server_default="dark"),
        sa.Column("grid_config", _json(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_layouts_user_id", "layouts", ["user_id"])

    op.create_table(
        "displays",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("device_type", device_type, nullable=False, server_default="browser"),
        sa.Column("status", display_status, nullable=False, server_default="unpaired"),
        sa.Column("pairing_code", sa.String(12)),
        sa.Column("group", sa.String(120)),
        sa.Column("last_seen", sa.DateTime(timezone=True)),
        sa.Column("current_layout_id", sa.Integer(), sa.ForeignKey("layouts.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_displays_user_id", "displays", ["user_id"])
    op.create_index("ix_displays_pairing_code", "displays", ["pairing_code"])
    op.create_index("ix_displays_group", "displays", ["group"])
    op.create_index("ix_displays_current_layout_id", "displays", ["current_layout_id"])

    op.create_table(
        "widgets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("layout_id", sa.Integer(), sa.ForeignKey("layouts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("widget_type", sa.String(64), nullable=False),
        sa.Column("config", _json(), nullable=False),
        sa.Column("position_x", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("position_y", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("width", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("height", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("width > 0", name="ck_widget_width_positive"),
        sa.CheckConstraint("height > 0", name="ck_widget_height_positive"),
        sa.CheckConstraint("position_x >= 0", name="ck_widget_x_nonneg"),
        sa.CheckConstraint("position_y >= 0", name="ck_widget_y_nonneg"),
    )
    op.create_index("ix_widgets_layout_id", "widgets", ["layout_id"])
    op.create_index("ix_widgets_widget_type", "widgets", ["widget_type"])

    op.create_table(
        "templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("category", sa.String(64), nullable=False, server_default="general"),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("definition", _json(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_templates_user_id", "templates", ["user_id"])


def downgrade() -> None:
    op.drop_table("templates")
    op.drop_table("widgets")
    op.drop_table("displays")
    op.drop_table("layouts")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    display_status.drop(op.get_bind(), checkfirst=True)
    device_type.drop(op.get_bind(), checkfirst=True)
