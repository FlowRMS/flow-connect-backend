"""add shipment requests tables

Revision ID: b2c3d4e5f6g7
Revises: 20251226_add_inventory
Create Date: 2025-12-26 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20251226_add_shipment_requests"
down_revision: str = "20251226_add_inventory"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create shipment_requests table
    op.create_table(
        "shipment_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "warehouse_id", postgresql.UUID(as_uuid=True), nullable=False, index=True
        ),
        sa.Column(
            "factory_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycore.companies.id"),
            nullable=True,
        ),
        sa.Column("status", sa.String(20), nullable=False, default="PENDING"),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("requested_delivery_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        schema="warehouse",
    )

    # Create shipment_request_items table
    op.create_table(
        "shipment_request_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "request_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("warehouse.shipment_requests.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("product_id", sa.String(100), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False, default=1),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        schema="warehouse",
    )


def downgrade() -> None:
    op.drop_table("shipment_request_items", schema="warehouse")
    op.drop_table("shipment_requests", schema="warehouse")
