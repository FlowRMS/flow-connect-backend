from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "warehouse_deliveries_001"
down_revision: str | None = "insert_default_job_statuses"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "recurring_shipments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor_contact_name", sa.String(255), nullable=True),
        sa.Column("vendor_contact_email", sa.String(255), nullable=True),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("carrier", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recurrence_pattern", postgresql.JSONB(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, default=1),
        sa.Column("last_generated_date", sa.Date(), nullable=True),
        sa.Column("next_expected_date", sa.Date(), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["vendor_id"],
            ["pycore.factories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["warehouse_id"],
            ["pywarehouse.warehouses.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )

    _ = op.create_table(
        "deliveries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("po_number", sa.String(50), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("carrier_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tracking_number", sa.String(255), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, default=1),
        sa.Column("expected_date", sa.Date(), nullable=True),
        sa.Column("arrived_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "receiving_started_at", postgresql.TIMESTAMP(timezone=True), nullable=True
        ),
        sa.Column("received_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "inventory_synced_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.Column("origin_address_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "destination_address_id", postgresql.UUID(as_uuid=True), nullable=True
        ),
        sa.Column("recurring_shipment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("vendor_contact_name", sa.String(255), nullable=True),
        sa.Column("vendor_contact_email", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["warehouse_id"],
            ["pywarehouse.warehouses.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["vendor_id"],
            ["pycore.factories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["carrier_id"],
            ["pywarehouse.shipping_carriers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["origin_address_id"],
            ["pycore.addresses.id"],
        ),
        sa.ForeignKeyConstraint(
            ["destination_address_id"],
            ["pycore.addresses.id"],
        ),
        sa.ForeignKeyConstraint(
            ["recurring_shipment_id"],
            ["pywarehouse.recurring_shipments.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["updated_by_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("po_number", name="uq_deliveries_po_number"),
        schema="pywarehouse",
    )

    _ = op.create_table(
        "delivery_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expected_quantity", sa.Integer(), nullable=False, default=0),
        sa.Column("received_quantity", sa.Integer(), nullable=False, default=0),
        sa.Column("damaged_quantity", sa.Integer(), nullable=False, default=0),
        sa.Column("status", sa.SmallInteger(), nullable=False, default=1),
        sa.Column("discrepancy_notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["delivery_id"],
            ["pywarehouse.deliveries.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["pycore.products.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )

    _ = op.create_table(
        "delivery_item_receipts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("receipt_type", sa.SmallInteger(), nullable=False, default=1),
        sa.Column("received_quantity", sa.Integer(), nullable=False, default=0),
        sa.Column("damaged_quantity", sa.Integer(), nullable=False, default=0),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("received_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("received_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["delivery_item_id"],
            ["pywarehouse.delivery_items.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["received_by_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )

    _ = op.create_table(
        "delivery_status_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.SmallInteger(), nullable=False),
        sa.Column(
            "timestamp",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["delivery_id"],
            ["pywarehouse.deliveries.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )

    _ = op.create_table(
        "delivery_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("receipt_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("issue_type", sa.SmallInteger(), nullable=False),
        sa.Column("custom_issue_type", sa.String(100), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, default=0),
        sa.Column("status", sa.SmallInteger(), nullable=False, default=1),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("communicated_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["delivery_id"],
            ["pywarehouse.deliveries.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["delivery_item_id"],
            ["pywarehouse.delivery_items.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["receipt_id"],
            ["pywarehouse.delivery_item_receipts.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )

    _ = op.create_table(
        "delivery_assignees",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.SmallInteger(), nullable=False),
        sa.ForeignKeyConstraint(
            ["delivery_id"],
            ["pywarehouse.deliveries.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )

    _ = op.create_table(
        "delivery_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("doc_type", sa.SmallInteger(), nullable=False),
        sa.Column("uploaded_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "uploaded_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["delivery_id"],
            ["pywarehouse.deliveries.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["file_id"],
            ["pyfiles.files.id"],
        ),
        sa.ForeignKeyConstraint(
            ["uploaded_by_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )


def downgrade() -> None:
    op.drop_table("delivery_documents", schema="pywarehouse")
    op.drop_table("delivery_assignees", schema="pywarehouse")
    op.drop_table("delivery_issues", schema="pywarehouse")
    op.drop_table("delivery_status_history", schema="pywarehouse")
    op.drop_table("delivery_item_receipts", schema="pywarehouse")
    op.drop_table("delivery_items", schema="pywarehouse")
    op.drop_table("deliveries", schema="pywarehouse")
    op.drop_table("recurring_shipments", schema="pywarehouse")
