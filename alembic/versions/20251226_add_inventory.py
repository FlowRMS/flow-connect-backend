from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str = "6e453caa5fb9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Create pywarehouse schema if not exists
    op.execute("CREATE SCHEMA IF NOT EXISTS pywarehouse")

    # Create warehouses table
    if not inspector.has_table("warehouses", schema="pywarehouse"):
        _ = op.create_table(
            "warehouses",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("status", sa.String(50), nullable=False, server_default="active"),
            sa.Column("latitude", sa.Numeric(10, 7), nullable=True),
            sa.Column("longitude", sa.Numeric(10, 7), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True, default=True),
            sa.Column(
                "created_at", sa.DateTime(timezone=False), server_default=sa.func.now()
            ),
            schema="pywarehouse",
        )

    # Create warehouse_locations table
    if not inspector.has_table("warehouse_locations", schema="pywarehouse"):
        _ = op.create_table(
            "warehouse_locations",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column(
                "warehouse_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pywarehouse.warehouses.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column("code", sa.Integer, nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column(
                "parent_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pywarehouse.warehouse_locations.id", ondelete="CASCADE"),
                nullable=True,
                index=True,
            ),
            sa.Column("full_path", sa.String(500), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
            # Audit columns
            sa.Column(
                "created_by_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pyuser.users.id"),
                nullable=True,
                index=True,
            ),
            sa.Column(
                "created_at", sa.DateTime(timezone=False), server_default=sa.func.now()
            ),
            schema="pywarehouse",
        )

    # Create inventory table
    if not inspector.has_table("inventory", schema="pywarehouse"):
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
                "warehouse_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pywarehouse.warehouses.id"),
                nullable=False,
                index=True,
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
                "created_by_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pyuser.users.id"),
                nullable=True,
                index=True,
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
            schema="pywarehouse",
        )

    # Create inventory_items table
    if not inspector.has_table("inventory_items", schema="pywarehouse"):
        _ = op.create_table(
            "inventory_items",
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column(
                "inventory_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pywarehouse.inventory.id", ondelete="CASCADE"),
                nullable=False,
                index=True,
            ),
            sa.Column(
                "location_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pywarehouse.warehouse_locations.id"),
                nullable=True,
                index=True,
            ),
            # Quantity as Numeric to match Decimal in model
            sa.Column("quantity", sa.Numeric, nullable=False, default=0),
            sa.Column("lot_number", sa.String(100), nullable=True),
            # IntEnum stored as Integer
            sa.Column("status", sa.Integer, nullable=False, default=1),
            sa.Column("received_date", sa.DateTime(timezone=False), nullable=True),
            # Audit columns
            sa.Column(
                "created_by_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("pyuser.users.id"),
                nullable=True,
                index=True,
            ),
            sa.Column(
                "created_at", sa.DateTime(timezone=False), server_default=sa.func.now()
            ),
            schema="pywarehouse",
        )


def downgrade() -> None:
    op.drop_table("inventory_items", schema="pywarehouse")
    op.drop_table("inventory", schema="pywarehouse")
    op.drop_table("warehouse_locations", schema="pywarehouse")
    op.drop_table("warehouses", schema="pywarehouse")
    op.execute("DROP SCHEMA IF EXISTS pywarehouse")
