"""revert orders sold_to_customer_id back to NOT NULL

Orders require sold_to_customer_id for commission and credit logic.
Only quotes and pre_opportunities should have optional sold_to_customer_id.

Revision ID: orders_sold_to_not_null
Revises: quotes_orders_sold_to_nullable
Create Date: 2026-01-28 16:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "orders_sold_to_not_null"
down_revision: str | None = "quotes_orders_sold_to_nullable"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Orders MUST have a sold_to_customer_id for commission/credit calculations
    # First, check if there are any NULL values that need to be handled
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM pycommission.orders WHERE sold_to_customer_id IS NULL
            ) THEN
                RAISE EXCEPTION 'Cannot make sold_to_customer_id NOT NULL: orders with NULL values exist. Please fix the data first.';
            END IF;
        END $$;
    """)

    op.alter_column(
        "orders",
        "sold_to_customer_id",
        existing_type=sa.UUID(),
        nullable=False,
        schema="pycommission",
    )


def downgrade() -> None:
    # Allow NULL sold_to_customer_id on orders (reverting to previous state)
    op.alter_column(
        "orders",
        "sold_to_customer_id",
        existing_type=sa.UUID(),
        nullable=True,
        schema="pycommission",
    )
