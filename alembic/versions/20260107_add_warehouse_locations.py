"""add warehouse locations tables

Revision ID: warehouse_locations_001
Revises: organizations_001
Create Date: 2026-01-07

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "warehouse_locations_001"
down_revision: str | None = "organizations_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create warehouse_locations table in pywarehouse schema
    _ = op.create_table(
        "warehouse_locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False),  # WarehouseStructureCode enum
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, default=0),
        # Visual properties for layout builder
        sa.Column("x", sa.Numeric(10, 2), nullable=True),
        sa.Column("y", sa.Numeric(10, 2), nullable=True),
        sa.Column("width", sa.Numeric(10, 2), nullable=True),
        sa.Column("height", sa.Numeric(10, 2), nullable=True),
        sa.Column("rotation", sa.Numeric(10, 2), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["warehouse_id"],
            ["pywarehouse.warehouses.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["pywarehouse.warehouse_locations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )

    # Create index on warehouse_id for faster lookups
    op.create_index(
        "ix_warehouse_locations_warehouse_id",
        "warehouse_locations",
        ["warehouse_id"],
        schema="pywarehouse",
    )

    # Create index on parent_id for faster tree traversal
    op.create_index(
        "ix_warehouse_locations_parent_id",
        "warehouse_locations",
        ["parent_id"],
        schema="pywarehouse",
    )

    # Create location_product_assignments table in pywarehouse schema
    _ = op.create_table(
        "location_product_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, default=0),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["location_id"],
            ["pywarehouse.warehouse_locations.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["pycore.products.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        # Unique constraint: same product can't be assigned to same location twice
        sa.UniqueConstraint("location_id", "product_id", name="uq_location_product"),
        schema="pywarehouse",
    )

    # Create index on location_id for faster lookups
    op.create_index(
        "ix_location_product_assignments_location_id",
        "location_product_assignments",
        ["location_id"],
        schema="pywarehouse",
    )

    # Create index on product_id for faster lookups
    op.create_index(
        "ix_location_product_assignments_product_id",
        "location_product_assignments",
        ["product_id"],
        schema="pywarehouse",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_location_product_assignments_product_id",
        table_name="location_product_assignments",
        schema="pywarehouse",
    )
    op.drop_index(
        "ix_location_product_assignments_location_id",
        table_name="location_product_assignments",
        schema="pywarehouse",
    )
    op.drop_table("location_product_assignments", schema="pywarehouse")

    op.drop_index(
        "ix_warehouse_locations_parent_id",
        table_name="warehouse_locations",
        schema="pywarehouse",
    )
    op.drop_index(
        "ix_warehouse_locations_warehouse_id",
        table_name="warehouse_locations",
        schema="pywarehouse",
    )
    op.drop_table("warehouse_locations", schema="pywarehouse")
