# merge all heads final
# Revision ID: e1824a0cf94c
# Revises: add_sales_teams, 51ec244363cf
# Create Date: 2026-02-03 11:19:07.596712
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "e1824a0cf94c"
down_revision: tuple[str, ...] | None = ("add_sales_teams", "51ec244363cf")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
