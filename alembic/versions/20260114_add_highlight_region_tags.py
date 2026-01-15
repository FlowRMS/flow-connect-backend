"""add_highlight_region_tags

Revision ID: highlight_tags_001
Revises: 7b633c60d91b
Create Date: 2026-01-14 19:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "highlight_tags_001"
down_revision: str | None = "7b633c60d91b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add tags array column to spec_sheet_highlight_regions table
    op.add_column(
        "spec_sheet_highlight_regions",
        sa.Column("tags", ARRAY(sa.String()), nullable=True),
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_column("spec_sheet_highlight_regions", "tags", schema="pycrm")
