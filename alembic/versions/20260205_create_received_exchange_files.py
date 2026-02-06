"""Create received_exchange_files table

Revision ID: 20260205_001
Revises: 20260130_002
Create Date: 2026-02-05 16:45:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260205_001"
down_revision: str | None = "20260130_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "received_exchange_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sender_org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("s3_key", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_sha", sa.String(64), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("reporting_period", sa.String(100), nullable=False),
        sa.Column("is_pos", sa.Boolean(), nullable=False),
        sa.Column("is_pot", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="new"),
        sa.Column(
            "received_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("s3_key", name="uq_received_exchange_files_s3_key"),
        schema="connect_pos",
    )

    op.create_index(
        "ix_received_exchange_files_org_id",
        "received_exchange_files",
        ["org_id"],
        schema="connect_pos",
    )
    op.create_index(
        "ix_received_exchange_files_sender_org_id",
        "received_exchange_files",
        ["sender_org_id"],
        schema="connect_pos",
    )
    op.create_index(
        "ix_received_exchange_files_status",
        "received_exchange_files",
        ["status"],
        schema="connect_pos",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_received_exchange_files_status",
        table_name="received_exchange_files",
        schema="connect_pos",
    )
    op.drop_index(
        "ix_received_exchange_files_sender_org_id",
        table_name="received_exchange_files",
        schema="connect_pos",
    )
    op.drop_index(
        "ix_received_exchange_files_org_id",
        table_name="received_exchange_files",
        schema="connect_pos",
    )
    op.drop_table("received_exchange_files", schema="connect_pos")
