"""merge_multiple_heads

Revision ID: d538c52154d8
Revises: 8a447991abdd, spec_sheet_file_id, add_chat_folders
Create Date: 2026-01-19 14:03:00.112936

"""

import os
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d538c52154d8"
down_revision: str | None = ("8a447991abdd", "spec_sheet_file_id", "add_chat_folders")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
