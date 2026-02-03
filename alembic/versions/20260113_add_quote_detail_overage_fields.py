"""add_quote_detail_overage_fields

Revision ID: 7b633c60d91b
Revises: 262a851d61ee
Create Date: 2026-01-13 15:18:49.110020

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7b633c60d91b"
down_revision: str | None = "262a851d61ee"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [
        col["name"] for col in inspector.get_columns("quote_details", schema="pycrm")
    ]

    # Add overage fields to quote_details table
    if "overage_commission_rate" not in columns:
        op.add_column(
            "quote_details",
            sa.Column("overage_commission_rate", sa.Numeric(18, 6), nullable=True),
            schema="pycrm",
        )
    if "overage_commission" not in columns:
        op.add_column(
            "quote_details",
            sa.Column("overage_commission", sa.Numeric(18, 6), nullable=True),
            schema="pycrm",
        )
    if "overage_unit_price" not in columns:
        op.add_column(
            "quote_details",
            sa.Column("overage_unit_price", sa.Numeric(18, 6), nullable=True),
            schema="pycrm",
        )
    if "fixture_schedule" not in columns:
        op.add_column(
            "quote_details",
            sa.Column("fixture_schedule", sa.String(50), nullable=True),
            schema="pycrm",
        )


def downgrade() -> None:
    op.drop_column("quote_details", "fixture_schedule", schema="pycrm")
    op.drop_column("quote_details", "overage_unit_price", schema="pycrm")
    op.drop_column("quote_details", "overage_commission", schema="pycrm")
    op.drop_column("quote_details", "overage_commission_rate", schema="pycrm")
