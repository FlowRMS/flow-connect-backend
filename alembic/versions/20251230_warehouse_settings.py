"""warehouse settings - create pywarehouse schema and warehouse tables

Revision ID: warehouse_settings_001
Revises: 62e4315e9e63
Create Date: 2024-12-30

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "warehouse_settings_001"
down_revision: str | None = "62e4315e9e63"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create pywarehouse schema
    op.execute("CREATE SCHEMA IF NOT EXISTS pywarehouse")

    # Create container_types table in pywarehouse schema
    op.create_table(
        "container_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("length", sa.Numeric(10, 2), nullable=False),
        sa.Column("width", sa.Numeric(10, 2), nullable=False),
        sa.Column("height", sa.Numeric(10, 2), nullable=False),
        sa.Column("weight", sa.Numeric(10, 2), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )

    # Create shipping_carriers table in pywarehouse schema
    op.create_table(
        "shipping_carriers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=True),
        sa.Column("account_number", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column("payment_terms", sa.String(50), nullable=True),
        sa.Column("api_key", sa.Text(), nullable=True),
        sa.Column("api_endpoint", sa.Text(), nullable=True),
        sa.Column("tracking_url_template", sa.String(500), nullable=True),
        sa.Column("service_types", postgresql.JSONB(), nullable=True),
        sa.Column("default_service_type", sa.String(100), nullable=True),
        sa.Column("max_weight", sa.Numeric(10, 2), nullable=True),
        sa.Column("max_dimensions", sa.String(50), nullable=True),
        sa.Column("residential_surcharge", sa.Numeric(10, 2), nullable=True),
        sa.Column("fuel_surcharge_percent", sa.Numeric(5, 2), nullable=True),
        sa.Column("pickup_schedule", sa.String(255), nullable=True),
        sa.Column("pickup_location", sa.String(255), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("internal_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )

    # Create warehouses table in pywarehouse schema
    op.create_table(
        "warehouses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 6), nullable=True),
        sa.Column("longitude", sa.Numeric(10, 6), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True, default=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )

    # Create warehouse_members table in pywarehouse schema
    op.create_table(
        "warehouse_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.Integer(), nullable=False),
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
            ["user_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )

    # Create warehouse_settings table in pywarehouse schema
    op.create_table(
        "warehouse_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("auto_generate_codes", sa.Boolean(), nullable=True, default=False),
        sa.Column("require_location", sa.Boolean(), nullable=True, default=True),
        sa.Column("show_in_pick_lists", sa.Boolean(), nullable=True, default=True),
        sa.Column("generate_qr_codes", sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(
            ["warehouse_id"],
            ["pywarehouse.warehouses.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("warehouse_id"),
        schema="pywarehouse",
    )

    # Create warehouse_structure table in pywarehouse schema
    op.create_table(
        "warehouse_structure",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.Integer(), nullable=False),
        sa.Column("level_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["warehouse_id"],
            ["pywarehouse.warehouses.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pywarehouse",
    )


def downgrade() -> None:
    op.drop_table("warehouse_structure", schema="pywarehouse")
    op.drop_table("warehouse_settings", schema="pywarehouse")
    op.drop_table("warehouse_members", schema="pywarehouse")
    op.drop_table("warehouses", schema="pywarehouse")
    op.drop_table("shipping_carriers", schema="pywarehouse")
    op.drop_table("container_types", schema="pywarehouse")
    op.execute("DROP SCHEMA IF EXISTS pywarehouse")
