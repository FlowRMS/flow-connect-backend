"""add factory overage fields

Revision ID: factory_overage_001
Revises: factory_plitem_quotes
Create Date: 2026-01-13 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "factory_overage_001"
down_revision: str | None = "submittals_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add overage_allowed boolean field
    op.add_column(
        "factories",
        sa.Column(
            "overage_allowed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        schema="pycore",
    )

    # Add overage_type field (0=BY_LINE, 1=BY_TOTAL)
    op.add_column(
        "factories",
        sa.Column(
            "overage_type",
            sa.SmallInteger(),
            nullable=False,
            server_default=sa.text("0"),  # BY_LINE default
        ),
        schema="pycore",
    )

    # Add rep_overage_share field (percentage 0-100)
    op.add_column(
        "factories",
        sa.Column(
            "rep_overage_share",
            sa.Numeric(5, 2),
            nullable=False,
            server_default=sa.text("100.00"),  # 100% default
        ),
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_column("factories", "rep_overage_share", schema="pycore")
    op.drop_column("factories", "overage_type", schema="pycore")
    op.drop_column("factories", "overage_allowed", schema="pycore")
