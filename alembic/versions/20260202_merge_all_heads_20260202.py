# merge_all_heads_20260202
# Revision ID: a9ce29443448
# Revises: 2482591dc2ad, 7702478b47b2
# Create Date: 2026-02-02 12:14:08.418978

from collections.abc import Sequence

revision: str = "a9ce29443448"
down_revision: tuple[str, ...] = ("2482591dc2ad", "7702478b47b2")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
