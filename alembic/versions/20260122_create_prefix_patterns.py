"""Create prefix_patterns table

Revision ID: 20260122_003
Revises: 20260122_002
Create Date: 2026-01-22 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260122_003"
down_revision: str | None = "20260122_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "prefix_patterns",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "name",
            name="uq_prefix_patterns_org_name",
        ),
        schema="connect_pos",
    )

    op.create_index(
        "ix_prefix_patterns_organization_id",
        "prefix_patterns",
        ["organization_id"],
        schema="connect_pos",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_prefix_patterns_organization_id",
        table_name="prefix_patterns",
        schema="connect_pos",
    )
    op.drop_table("prefix_patterns", schema="connect_pos")
