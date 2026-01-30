"""merge_freight_categories_and_entity_watchers

Revision ID: 7702478b47b2
Revises: add_freight_categories, add_entity_watchers
Create Date: 2026-01-30 17:44:07.624835

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "7702478b47b2"
down_revision: tuple[str, str] = ("add_freight_categories", "add_entity_watchers")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
