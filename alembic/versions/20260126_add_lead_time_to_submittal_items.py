# add lead_time to submittal_items
# Revision ID: add_lead_time_to_items
# Revises: add_returned_pdf_tables
# Create Date: 2026-01-26

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_lead_time_to_items"
down_revision: str | None = "add_returned_pdf_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "submittal_items",
        sa.Column("lead_time", sa.String(100), nullable=True),
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_column("submittal_items", "lead_time", schema="pycrm")
