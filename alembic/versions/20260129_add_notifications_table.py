"""add notifications table

Revision ID: add_notifications_table
Revises: quotes_orders_sold_to_nullable, factory_plitem_orders
Create Date: 2026-01-29

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_notifications_table"
down_revision: tuple[str, ...] = (
    "quotes_orders_sold_to_nullable",
    "factory_plitem_orders",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names(schema="pycore")

    if "notifications" in tables:
        return

    _ = op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("entity_type", sa.Integer(), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("notification_type", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("read_at", sa.TIMESTAMP(timezone=True), nullable=True),
        schema="pycore",
    )

    op.create_index(
        "ix_notifications_user_id",
        "notifications",
        ["user_id"],
        schema="pycore",
    )
    op.create_index(
        "ix_notifications_user_is_read",
        "notifications",
        ["user_id", "is_read"],
        schema="pycore",
    )
    op.create_index(
        "ix_notifications_created_at_desc",
        "notifications",
        [sa.text("created_at DESC")],
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_index("ix_notifications_created_at_desc", "notifications", schema="pycore")
    op.drop_index("ix_notifications_user_is_read", "notifications", schema="pycore")
    op.drop_index("ix_notifications_user_id", "notifications", schema="pycore")
    op.drop_table("notifications", schema="pycore")
