"""adding reasoning to pending_document_correction_changes

Revision ID: c44a69ade93f
Revises: e9cbe792b9d3
Create Date: 2026-01-20 17:21:59.772714

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c44a69ade93f"
down_revision: str | None = "e9cbe792b9d3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "pending_document_correction_changes",
        sa.Column("reasoning", sa.Text(), nullable=True),
        schema="ai",
    )


def downgrade() -> None:
    op.drop_column("pending_document_correction_changes", "reasoning", schema="ai")
