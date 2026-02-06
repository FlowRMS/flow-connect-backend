"""Add validation_status to exchange_files and create file_validation_issues table

Revision ID: 20260126_001
Revises: 20260123_001
Create Date: 2026-01-26 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260126_001"
down_revision: str | None = "20260123_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "exchange_files",
        sa.Column(
            "validation_status",
            sa.String(20),
            nullable=False,
            server_default="not_validated",
        ),
        schema="connect_pos",
    )
    op.create_index(
        "ix_exchange_files_validation_status",
        "exchange_files",
        ["validation_status"],
        schema="connect_pos",
    )

    op.create_table(
        "file_validation_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exchange_file_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("column_name", sa.String(100), nullable=True),
        sa.Column("validation_key", sa.String(50), nullable=False),
        sa.Column("message", sa.String(500), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["exchange_file_id"],
            ["connect_pos.exchange_files.id"],
            ondelete="CASCADE",
        ),
        schema="connect_pos",
    )
    op.create_index(
        "ix_file_validation_issues_exchange_file_id",
        "file_validation_issues",
        ["exchange_file_id"],
        schema="connect_pos",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_file_validation_issues_exchange_file_id",
        table_name="file_validation_issues",
        schema="connect_pos",
    )
    op.drop_table("file_validation_issues", schema="connect_pos")

    op.drop_index(
        "ix_exchange_files_validation_status",
        table_name="exchange_files",
        schema="connect_pos",
    )
    op.drop_column("exchange_files", "validation_status", schema="connect_pos")
