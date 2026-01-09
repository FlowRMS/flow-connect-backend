"""merge_multiple_heads

Revision ID: 211a23a26864
Revises: 22af57481162, 20260106_carrier_type, 896105b07ca6
Create Date: 2026-01-08 19:36:23.921272

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "211a23a26864"
down_revision: tuple[str, ...] = (
    "22af57481162",
    "20260106_carrier_type",
    "896105b07ca6",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
