"""Create connection_territories table

Revision ID: 20260127_002
Revises: 20260127_001
Create Date: 2026-01-27 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260127_002"
down_revision: str | None = "20260127_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "connection_territories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("connection_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subdivision_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["subdivision_id"],
            ["connect_geography.subdivisions.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "connection_id",
            "subdivision_id",
            name="uq_connection_territory",
        ),
        schema="connect_pos",
    )

    op.create_index(
        "ix_connection_territories_connection_id",
        "connection_territories",
        ["connection_id"],
        schema="connect_pos",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_connection_territories_connection_id",
        table_name="connection_territories",
        schema="connect_pos",
    )
    op.drop_table("connection_territories", schema="connect_pos")
