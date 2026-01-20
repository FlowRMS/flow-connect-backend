"""merge_spec_sheet_folders_and_highlight_tags

Revision ID: 96d32cf858d0
Revises: highlight_tags_001, create_spec_sheet_folders
Create Date: 2026-01-19 15:12:18.955205

"""

import os
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "96d32cf858d0"
down_revision: str | None = ("highlight_tags_001", "create_spec_sheet_folders")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
