"""add entity_watchers table

Revision ID: add_entity_watchers
Revises: 14c956003e6b
Create Date: 2026-01-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_entity_watchers"
down_revision: str | None = "14c956003e6b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "entity_watchers",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), nullable=False, primary_key=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("entity_type", sa.SmallInteger(), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "entity_type",
            "entity_id",
            "user_id",
            name="uq_entity_watchers_entity_user",
        ),
        schema="pycrm",
    )

    op.create_index(
        "ix_entity_watchers_user_id",
        "entity_watchers",
        ["user_id"],
        schema="pycrm",
    )
    op.create_index(
        "ix_entity_watchers_entity",
        "entity_watchers",
        ["entity_type", "entity_id"],
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_entity_watchers_entity", table_name="entity_watchers", schema="pycrm"
    )
    op.drop_index(
        "ix_entity_watchers_user_id", table_name="entity_watchers", schema="pycrm"
    )
    op.drop_table("entity_watchers", schema="pycrm")
