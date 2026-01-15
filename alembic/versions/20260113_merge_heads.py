"""merge_heads

Revision ID: 262a851d61ee
Revises: b2c3d4e5f607, factory_overage_001
Create Date: 2026-01-13 15:16:42.227951

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "262a851d61ee"
down_revision: tuple[str, str] = ("b2c3d4e5f607", "factory_overage_001")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
