"""merge all migration heads

Revision ID: merge_all_heads_20260202
Revises: 7702478b47b2, undo_null_sold_to, add_overage_fields
Create Date: 2026-02-02 18:00:00.000000

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "merge_all_heads_20260202"
down_revision: tuple[str, ...] = ("7702478b47b2", "undo_null_sold_to", "add_overage_fields")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
