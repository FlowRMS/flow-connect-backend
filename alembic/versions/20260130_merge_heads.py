"""Merge migration heads 20260126_001 and 20260128_001.

Revision ID: 20260130_001
Revises: 20260126_001, 20260128_001
Create Date: 2026-01-30

"""

from collections.abc import Sequence

revision: str = "20260130_001"
down_revision: tuple[str, str] = ("20260126_001", "20260128_001")
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
