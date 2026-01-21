"""add custom_prompt column to nemra_notes_ai_summary table

Revision ID: b2c3d4e5f6a7
Revises: f6e5d4c3b2a1
Create Date: 2025-12-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "f6e5d4c3b2a1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "nemra_notes_ai_summary",
        sa.Column("custom_prompt", sa.Text(), nullable=True),
        schema="report",
    )


def downgrade() -> None:
    op.drop_column("nemra_notes_ai_summary", "custom_prompt", schema="report")
