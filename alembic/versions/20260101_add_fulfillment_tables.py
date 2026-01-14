"""Add fulfillment tables

Revision ID: fulfillment_001
Revises: warehouse_settings_001
Create Date: 2026-01-01

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fulfillment_001"
down_revision: str | None = "b2c3d4e5f607"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Fulfillment Orders
    _ = op.create_table(
        "fulfillment_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("fulfillment_order_number", sa.String(50), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("carrier_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column(
            "fulfillment_method", sa.SmallInteger(), nullable=False, server_default="1"
        ),
        sa.Column("carrier_type", sa.SmallInteger(), nullable=True),
        sa.Column("ship_to_address", postgresql.JSONB(), nullable=True),
        sa.Column("need_by_date", sa.Date(), nullable=True),
        sa.Column("released_at", sa.DateTime(), nullable=True),
        sa.Column("pick_started_at", sa.DateTime(), nullable=True),
        sa.Column("pick_completed_at", sa.DateTime(), nullable=True),
        sa.Column("pack_completed_at", sa.DateTime(), nullable=True),
        sa.Column("ship_confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("delivered_at", sa.DateTime(), nullable=True),
        sa.Column("tracking_numbers", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("bol_number", sa.String(100), nullable=True),
        sa.Column("pro_number", sa.String(100), nullable=True),
        sa.Column("pickup_signature", sa.Text(), nullable=True),
        sa.Column("pickup_timestamp", sa.DateTime(), nullable=True),
        sa.Column("pickup_customer_name", sa.String(255), nullable=True),
        sa.Column("driver_name", sa.String(255), nullable=True),
        sa.Column(
            "has_backorder_items", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column("hold_reason", sa.Text(), nullable=True),
        sa.Column("backorder_review_data", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["order_id"], ["pycommission.orders.id"]),
        sa.ForeignKeyConstraint(["warehouse_id"], ["pywarehouse.warehouses.id"]),
        sa.ForeignKeyConstraint(["carrier_id"], ["pywarehouse.shipping_carriers.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["pyuser.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )
    op.create_index(
        "ix_fulfillment_orders_order_id",
        "fulfillment_orders",
        ["order_id"],
        schema="pywarehouse",
    )
    op.create_index(
        "ix_fulfillment_orders_warehouse_id",
        "fulfillment_orders",
        ["warehouse_id"],
        schema="pywarehouse",
    )
    op.create_index(
        "ix_fulfillment_orders_status",
        "fulfillment_orders",
        ["status"],
        schema="pywarehouse",
    )
    op.create_unique_constraint(
        "uq_fulfillment_order_number",
        "fulfillment_orders",
        ["fulfillment_order_number"],
        schema="pywarehouse",
    )

    # Fulfillment Order Line Items
    _ = op.create_table(
        "fulfillment_order_line_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "fulfillment_order_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("order_detail_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "ordered_qty",
            sa.Numeric(18, 4),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "allocated_qty",
            sa.Numeric(18, 4),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "picked_qty",
            sa.Numeric(18, 4),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "packed_qty",
            sa.Numeric(18, 4),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "shipped_qty",
            sa.Numeric(18, 4),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "backorder_qty",
            sa.Numeric(18, 4),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "fulfilled_by_manufacturer",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("manufacturer_fulfillment_status", sa.String(50), nullable=True),
        sa.Column(
            "linked_shipment_request_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("short_reason", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["fulfillment_order_id"],
            ["pywarehouse.fulfillment_orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["order_detail_id"], ["pycommission.order_details.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["pycore.products.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )
    op.create_index(
        "ix_fulfillment_line_items_order_id",
        "fulfillment_order_line_items",
        ["fulfillment_order_id"],
        schema="pywarehouse",
    )

    # Fulfillment Assignments
    _ = op.create_table(
        "fulfillment_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "fulfillment_order_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.SmallInteger(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["fulfillment_order_id"],
            ["pywarehouse.fulfillment_orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["pyuser.users.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["pyuser.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )
    op.create_index(
        "ix_fulfillment_assignments_order_id",
        "fulfillment_assignments",
        ["fulfillment_order_id"],
        schema="pywarehouse",
    )

    # Fulfillment Activities
    _ = op.create_table(
        "fulfillment_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "fulfillment_order_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("activity_type", sa.SmallInteger(), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["fulfillment_order_id"],
            ["pywarehouse.fulfillment_orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["created_by_id"], ["pyuser.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )
    op.create_index(
        "ix_fulfillment_activities_order_id",
        "fulfillment_activities",
        ["fulfillment_order_id"],
        schema="pywarehouse",
    )

    # Packing Boxes
    _ = op.create_table(
        "packing_boxes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "fulfillment_order_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("container_type_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("box_number", sa.Integer(), nullable=False),
        sa.Column("length", sa.Numeric(10, 2), nullable=True),
        sa.Column("width", sa.Numeric(10, 2), nullable=True),
        sa.Column("height", sa.Numeric(10, 2), nullable=True),
        sa.Column("weight", sa.Numeric(10, 2), nullable=True),
        sa.Column("tracking_number", sa.String(100), nullable=True),
        sa.Column("label_printed_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["fulfillment_order_id"],
            ["pywarehouse.fulfillment_orders.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["container_type_id"], ["pywarehouse.container_types.id"]
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )
    op.create_index(
        "ix_packing_boxes_order_id",
        "packing_boxes",
        ["fulfillment_order_id"],
        schema="pywarehouse",
    )

    # Packing Box Items
    _ = op.create_table(
        "packing_box_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("packing_box_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "fulfillment_line_item_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.ForeignKeyConstraint(
            ["packing_box_id"],
            ["pywarehouse.packing_boxes.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["fulfillment_line_item_id"],
            ["pywarehouse.fulfillment_order_line_items.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )
    op.create_index(
        "ix_packing_box_items_box_id",
        "packing_box_items",
        ["packing_box_id"],
        schema="pywarehouse",
    )


def downgrade() -> None:
    op.drop_table("packing_box_items", schema="pywarehouse")
    op.drop_table("packing_boxes", schema="pywarehouse")
    op.drop_table("fulfillment_activities", schema="pywarehouse")
    op.drop_table("fulfillment_assignments", schema="pywarehouse")
    op.drop_table("fulfillment_order_line_items", schema="pywarehouse")
    op.drop_table("fulfillment_orders", schema="pywarehouse")
