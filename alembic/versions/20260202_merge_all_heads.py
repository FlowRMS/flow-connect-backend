"""merge all migration heads

Revision ID: merge_all_heads_20260202
Revises: undo_null_sold_to, add_factory_parent_child, add_role_detail_contacts
Create Date: 2026-02-02 18:00:00.000000

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "merge_all_heads_20260202"
down_revision: tuple[str, ...] = (
    "undo_null_sold_to",
    "add_factory_parent_child",
    "add_role_detail_contacts",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
