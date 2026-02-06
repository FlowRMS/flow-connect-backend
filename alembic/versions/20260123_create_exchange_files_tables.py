"""Create exchange_files and exchange_file_target_orgs tables

Revision ID: 20260123_001
Revises: 20260122_003
Create Date: 2026-01-23 09:45:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260123_001"
down_revision: str | None = "20260122_003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "exchange_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("s3_key", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("file_sha", sa.String(64), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("reporting_period", sa.String(100), nullable=False),
        sa.Column("is_pos", sa.Boolean(), nullable=False),
        sa.Column("is_pot", sa.Boolean(), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="connect_pos",
    )

    op.create_index(
        "ix_exchange_files_org_id",
        "exchange_files",
        ["org_id"],
        schema="connect_pos",
    )
    op.create_index(
        "ix_exchange_files_file_sha",
        "exchange_files",
        ["file_sha"],
        schema="connect_pos",
    )
    op.create_index(
        "ix_exchange_files_status",
        "exchange_files",
        ["status"],
        schema="connect_pos",
    )

    op.create_table(
        "exchange_file_target_orgs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exchange_file_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("connected_org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["exchange_file_id"],
            ["connect_pos.exchange_files.id"],
            ondelete="CASCADE",
        ),
        schema="connect_pos",
    )

    op.create_index(
        "ix_exchange_file_target_orgs_file_id",
        "exchange_file_target_orgs",
        ["exchange_file_id"],
        schema="connect_pos",
    )
    op.create_index(
        "ix_exchange_file_target_orgs_org_id",
        "exchange_file_target_orgs",
        ["connected_org_id"],
        schema="connect_pos",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_exchange_file_target_orgs_org_id",
        table_name="exchange_file_target_orgs",
        schema="connect_pos",
    )
    op.drop_index(
        "ix_exchange_file_target_orgs_file_id",
        table_name="exchange_file_target_orgs",
        schema="connect_pos",
    )
    op.drop_table("exchange_file_target_orgs", schema="connect_pos")

    op.drop_index(
        "ix_exchange_files_status",
        table_name="exchange_files",
        schema="connect_pos",
    )
    op.drop_index(
        "ix_exchange_files_file_sha",
        table_name="exchange_files",
        schema="connect_pos",
    )
    op.drop_index(
        "ix_exchange_files_org_id",
        table_name="exchange_files",
        schema="connect_pos",
    )
    op.drop_table("exchange_files", schema="connect_pos")
