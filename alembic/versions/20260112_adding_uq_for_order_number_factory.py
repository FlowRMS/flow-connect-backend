"""adding uq for order number_factory

Revision ID: a345ab2dcc2e
Revises: uq_invoice_adjustment_number
Create Date: 2026-01-12 09:36:32.411996

"""

from collections.abc import Sequence

from sqlalchemy import text

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a345ab2dcc2e"
down_revision: str | None = "uq_invoice_adjustment_number"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def constraint_exists(constraint_name: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        text("""
            SELECT 1 FROM pg_constraint
            WHERE conname = :name
        """),
        {"name": constraint_name},
    )
    return result.fetchone() is not None


def upgrade() -> None:
    if not constraint_exists("uc_orders_order_number_customer_id"):
        # Deduplicate order_number + sold_to_customer_id by appending -1, -2, etc.
        op.execute("""
            WITH duplicates AS (
                SELECT
                    id,
                    order_number,
                    sold_to_customer_id,
                    ROW_NUMBER() OVER (
                        PARTITION BY order_number, sold_to_customer_id
                        ORDER BY created_at, id
                    ) AS rn
                FROM pycommission.orders
            )
            UPDATE pycommission.orders o
            SET order_number = o.order_number || '-' || (d.rn - 1)::text
            FROM duplicates d
            WHERE o.id = d.id AND d.rn > 1
        """)

        op.create_unique_constraint(
            "uc_orders_order_number_customer_id",
            "orders",
            ["order_number", "sold_to_customer_id"],
            schema="pycommission",
        )


def downgrade() -> None:
    op.drop_constraint(
        "uc_orders_order_number_customer_id",
        "orders",
        type_="unique",
        schema="pycommission",
    )
