# merge overage and contacts heads
# Revision ID: 51ec244363cf
# Revises: factory_overage_001, add_role_detail_contacts
# Create Date: 2026-02-03 11:12:59.600763
from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "51ec244363cf"
down_revision: tuple[str, ...] | None = ("factory_overage_001", "add_role_detail_contacts")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
