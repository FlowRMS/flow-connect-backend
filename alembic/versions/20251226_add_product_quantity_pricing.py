"""add product_quantity_pricing table

Revision ID: 8a3f2c1d5e9b
Revises: 6b9c4d3e2f1a
Create Date: 2025-12-26 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "8a3f2c1d5e9b"
down_revision: str | None = "6b9c4d3e2f1a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "product_quantity_pricing",
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("quantity_low", sa.Numeric(), nullable=False),
        sa.Column("quantity_high", sa.Numeric(), nullable=False),
        sa.Column("unit_price", sa.Numeric(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["pycore.products.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycore",
    )
    op.create_index(
        op.f("ix_pycore_product_quantity_pricing_product_id"),
        "product_quantity_pricing",
        ["product_id"],
        unique=False,
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_pycore_product_quantity_pricing_product_id"),
        table_name="product_quantity_pricing",
        schema="pycore",
    )
    op.drop_table("product_quantity_pricing", schema="pycore")