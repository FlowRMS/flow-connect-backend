"""add inventory tables

Revision ID: a1b2c3d4e5f6
Revises: 20251225_add_customer_factory_sales_reps
Create Date: 2025-12-26 11:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20251226_add_inventory"
down_revision: str = "20251225_add_customer_factory_sales_reps"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create warehouse schema if not exists
    op.execute("CREATE SCHEMA IF NOT EXISTS warehouse")

    # Create inventory table
    _ = op.create_table(
        "inventory",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycore.products.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "warehouse_id", postgresql.UUID(as_uuid=True), nullable=False, index=True
        ),
        # Quantities as Numeric to match Decimal in model
        sa.Column("total_quantity", sa.Numeric, nullable=False, default=0),
        sa.Column("available_quantity", sa.Numeric, nullable=False, default=0),
        sa.Column("reserved_quantity", sa.Numeric, nullable=False, default=0),
        sa.Column("picking_quantity", sa.Numeric, nullable=False, default=0),
        # IntEnum stored as Integer
        sa.Column("ownership_type", sa.Integer, nullable=False, default=1),
        sa.Column("abc_class", sa.Integer, nullable=True),
        # Audit columns
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycore.users.id"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=False), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        schema="warehouse",
    )

    # Create inventory_items table
    _ = op.create_table(
        "inventory_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "inventory_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("warehouse.inventory.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("bin_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("bin_location", sa.String(255), nullable=True),
        sa.Column("full_location_path", sa.String(500), nullable=True),
        # Quantity as Numeric to match Decimal in model
        sa.Column("quantity", sa.Numeric, nullable=False, default=0),
        sa.Column("lot_number", sa.String(100), nullable=True),
        # IntEnum stored as Integer
        sa.Column("status", sa.Integer, nullable=False, default=1),
        sa.Column("received_date", sa.DateTime(timezone=False), nullable=True),
        # Audit columns
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycore.users.id"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=False), server_default=sa.func.now()
        ),
        schema="warehouse",
    )


def downgrade() -> None:
    op.drop_table("inventory_items", schema="warehouse")
    op.drop_table("inventory", schema="warehouse")
    op.execute("DROP SCHEMA IF EXISTS warehouse")
