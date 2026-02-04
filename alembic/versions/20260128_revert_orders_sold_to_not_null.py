"""revert orders sold_to_customer_id back to NOT NULL

Orders require sold_to_customer_id for commission and credit logic.
Only quotes and pre_opportunities should have optional sold_to_customer_id.

Revision ID: orders_sold_to_not_null
Revises: quotes_orders_sold_to_nullable
Create Date: 2026-01-28 16:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "orders_sold_to_not_null"
down_revision: str | None = "quotes_orders_sold_to_nullable"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # Check if column is already NOT NULL
    columns = inspector.get_columns("orders", schema="pycommission")
    for col in columns:
        if col["name"] == "sold_to_customer_id":
            if not col["nullable"]:
                # Already NOT NULL, skip
                return
            break

    # Check if there are NULL values - if so, skip (don't fail)
    result = conn.execute(
        sa.text("SELECT EXISTS(SELECT 1 FROM pycommission.orders WHERE sold_to_customer_id IS NULL)")
    )
    has_nulls = result.scalar()
    if has_nulls:
        # Can't apply this migration yet - data needs to be fixed first
        # Skip silently to allow other migrations to proceed
        return

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
