"""Add job_location, bid_date, and tags fields to submittals.

Revision ID: add_submittal_settings_fields
Revises: drop_spec_sheet_folder_path
Create Date: 2026-01-20 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_submittal_settings_fields"
down_revision: Union[str, None] = "drop_spec_sheet_folder_path"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add job_location, bid_date, and tags columns to submittals table."""
    # Add job_location column
    op.add_column(
        "submittals",
        sa.Column("job_location", sa.Text(), nullable=True),
        schema="pycrm",
    )

    # Add bid_date column
    op.add_column(
        "submittals",
        sa.Column("bid_date", sa.Date(), nullable=True),
        schema="pycrm",
    )

    # Add tags column (array of text)
    op.add_column(
        "submittals",
        sa.Column("tags", postgresql.ARRAY(sa.Text()), nullable=True),
        schema="pycrm",
    )


def downgrade() -> None:
    """Remove job_location, bid_date, and tags columns from submittals table."""
    op.drop_column("submittals", "tags", schema="pycrm")
    op.drop_column("submittals", "bid_date", schema="pycrm")
    op.drop_column("submittals", "job_location", schema="pycrm")
