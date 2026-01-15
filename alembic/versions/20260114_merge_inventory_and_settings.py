"""merge_inventory_and_settings

Revision ID: 7c44527b01d1
Revises: b2c3d4e5f607, add_general_settings
Create Date: 2026-01-14 12:33:58.910616

"""

from collections.abc import Sequence
from typing import Any

# revision identifiers, used by Alembic.
revision: str = "7c44527b01d1"
down_revision: Any | None = ("b2c3d4e5f607", "add_general_settings")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
