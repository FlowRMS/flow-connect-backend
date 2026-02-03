"""make sold_to_customer_id nullable on quotes and orders

Revision ID: quotes_orders_sold_to_nullable
Revises: add_name_to_quotes
Create Date: 2026-01-27 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "quotes_orders_sold_to_nullable"
down_revision: str | None = "add_name_to_quotes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Allow NULL sold_to_customer_id on quotes (for companies that aren't customers)
    op.alter_column(
        "quotes",
        "sold_to_customer_id",
        existing_type=sa.UUID(),
        nullable=True,
        schema="pycrm",
    )

    # Allow NULL sold_to_customer_id on orders (for companies that aren't customers)
    op.alter_column(
        "orders",
        "sold_to_customer_id",
        existing_type=sa.UUID(),
        nullable=True,
        schema="pycommission",
    )


def downgrade() -> None:
    # Handle NULL values before making columns NOT NULL
    op.execute("""
        UPDATE pycommission.orders
        SET sold_to_customer_id = (SELECT id FROM pycore.customers LIMIT 1)
        WHERE sold_to_customer_id IS NULL
    """)
    op.alter_column(
        "orders",
        "sold_to_customer_id",
        existing_type=sa.UUID(),
        nullable=False,
        schema="pycommission",
    )

    op.execute("""
        UPDATE pycrm.quotes
        SET sold_to_customer_id = (SELECT id FROM pycore.customers LIMIT 1)
        WHERE sold_to_customer_id IS NULL
    """)
    op.alter_column(
        "quotes",
        "sold_to_customer_id",
        existing_type=sa.UUID(),
        nullable=False,
        schema="pycrm",
    )
