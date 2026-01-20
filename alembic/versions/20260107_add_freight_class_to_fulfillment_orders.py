"""Add freight_class to fulfillment_orders.

Revision ID: 20260107_freight_class
Revises: 20260107_documents
Create Date: 2026-01-07

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260107_freight_class"
down_revision = "20260107_documents"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add freight_class column to fulfillment_orders
    op.add_column(
        "fulfillment_orders",
        sa.Column("freight_class", sa.String(10), nullable=True),
        schema="pywarehouse",
    )


def downgrade() -> None:
    # Remove freight_class column
    op.drop_column("fulfillment_orders", "freight_class", schema="pywarehouse")
