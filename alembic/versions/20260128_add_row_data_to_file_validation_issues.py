"""Add row_data column to file_validation_issues table

Revision ID: 20260128_001
Revises: 20260127_002
Create Date: 2026-01-28 14:10:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260128_001"
down_revision: str | None = "20260127_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "file_validation_issues",
        sa.Column("row_data", postgresql.JSONB, nullable=True),
        schema="connect_pos",
    )


def downgrade() -> None:
    op.drop_column("file_validation_issues", "row_data", schema="connect_pos")
