# merge_all_heads
# Revision ID: 2482591dc2ad
# Revises: a4dc14d8d606, 14c956003e6b
# Create Date: 2026-01-30 14:02:34.223251
import os
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2482591dc2ad"
down_revision: str | None = ("a4dc14d8d606", "14c956003e6b")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
