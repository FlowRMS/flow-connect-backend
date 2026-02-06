"""Create connect_pos schema and agreements table

Revision ID: 20260116_001
Revises:
Create Date: 2026-01-16 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260116_001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS connect_pos")

    op.create_table(
        "agreements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("connected_org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("s3_key", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_sha", sa.String(64), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("connected_org_id", name="uq_agreements_connected_org_id"),
        schema="connect_pos",
    )


def downgrade() -> None:
    op.drop_table("agreements", schema="connect_pos")
    op.execute("DROP SCHEMA IF EXISTS connect_pos")
