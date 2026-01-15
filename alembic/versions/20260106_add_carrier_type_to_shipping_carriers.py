"""Add carrier_type column to shipping_carriers table.

Revision ID: 20260106_carrier_type
Revises: add_fulfillment_002
Create Date: 2026-01-06

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260106_carrier_type"
down_revision = "add_fulfillment_002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add carrier_type column to shipping_carriers table
    # CarrierType enum: 1 = PARCEL, 2 = FREIGHT
    op.add_column(
        "shipping_carriers",
        sa.Column("carrier_type", sa.Integer(), nullable=True),
        schema="pywarehouse",
    )


def downgrade() -> None:
    op.drop_column("shipping_carriers", "carrier_type", schema="pywarehouse")
