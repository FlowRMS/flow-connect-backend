# add manufacturer to submittal_items
# Revision ID: add_manufacturer_to_items
# Revises: add_submittal_revision_tracking
# Create Date: 2026-01-20

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_manufacturer_to_items"
down_revision: str | None = "add_submittal_revision_tracking"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "submittal_items",
        sa.Column("manufacturer", sa.String(length=255), nullable=True),
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_column("submittal_items", "manufacturer", schema="pycrm")
