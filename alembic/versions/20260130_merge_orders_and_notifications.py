"""merge_orders_and_notifications

Revision ID: 14c956003e6b
Revises: orders_sold_to_not_null, add_notifications_table
Create Date: 2026-01-30 11:43:12.669908

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "14c956003e6b"
down_revision: tuple[str, ...] = ("orders_sold_to_not_null", "add_notifications_table")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
