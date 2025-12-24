"""warehouse settings - add shipping carrier columns and warehouse locations table

Revision ID: a1b2c3d4e5f6
Revises: 891079fe3cd6
Create Date: 2024-12-24

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "891079fe3cd6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add columns to shipping_carriers table
    op.add_column(
        "shipping_carriers",
        sa.Column("code", sa.String(length=50), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("billing_address", sa.Text(), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("payment_terms", sa.String(length=50), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("api_key", sa.String(length=255), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("api_endpoint", sa.String(length=500), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("tracking_url_template", sa.String(length=500), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("contact_name", sa.String(length=255), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("contact_phone", sa.String(length=50), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("service_types", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("default_service_type", sa.String(length=100), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("max_weight", sa.Numeric(precision=10, scale=2), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("max_dimensions", sa.String(length=50), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("residential_surcharge", sa.Numeric(precision=10, scale=2), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("fuel_surcharge_percent", sa.Numeric(precision=5, scale=2), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("pickup_schedule", sa.String(length=255), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("pickup_location", sa.String(length=255), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("remarks", sa.Text(), nullable=True),
        schema="pycrm",
    )
    op.add_column(
        "shipping_carriers",
        sa.Column("internal_notes", sa.Text(), nullable=True),
        schema="pycrm",
    )

    # Create warehouse_locations table
    _ = op.create_table(
        "warehouse_locations",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("warehouse_id", sa.UUID(), nullable=False),
        sa.Column("parent_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "type",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=True),
        sa.Column("x", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("y", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("width", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("height", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("rotation", sa.Numeric(precision=5, scale=2), server_default=sa.text("0"), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["warehouse_id"],
            ["pycrm.warehouses.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["pycrm.warehouse_locations.id"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "type IN ('section', 'aisle', 'shelf', 'bay', 'row', 'bin')",
            name="ck_warehouse_locations_type",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )
    op.create_index(
        "ix_warehouse_locations_warehouse_id",
        "warehouse_locations",
        ["warehouse_id"],
        unique=False,
        schema="pycrm",
    )
    op.create_index(
        "ix_warehouse_locations_parent_id",
        "warehouse_locations",
        ["parent_id"],
        unique=False,
        schema="pycrm",
    )
    op.create_index(
        "ix_warehouse_locations_type",
        "warehouse_locations",
        ["type"],
        unique=False,
        schema="pycrm",
    )


def downgrade() -> None:
    # Drop warehouse_locations table
    op.drop_index("ix_warehouse_locations_type", table_name="warehouse_locations", schema="pycrm")
    op.drop_index("ix_warehouse_locations_parent_id", table_name="warehouse_locations", schema="pycrm")
    op.drop_index("ix_warehouse_locations_warehouse_id", table_name="warehouse_locations", schema="pycrm")
    op.drop_table("warehouse_locations", schema="pycrm")

    # Remove columns from shipping_carriers
    op.drop_column("shipping_carriers", "internal_notes", schema="pycrm")
    op.drop_column("shipping_carriers", "remarks", schema="pycrm")
    op.drop_column("shipping_carriers", "pickup_location", schema="pycrm")
    op.drop_column("shipping_carriers", "pickup_schedule", schema="pycrm")
    op.drop_column("shipping_carriers", "fuel_surcharge_percent", schema="pycrm")
    op.drop_column("shipping_carriers", "residential_surcharge", schema="pycrm")
    op.drop_column("shipping_carriers", "max_dimensions", schema="pycrm")
    op.drop_column("shipping_carriers", "max_weight", schema="pycrm")
    op.drop_column("shipping_carriers", "default_service_type", schema="pycrm")
    op.drop_column("shipping_carriers", "service_types", schema="pycrm")
    op.drop_column("shipping_carriers", "contact_email", schema="pycrm")
    op.drop_column("shipping_carriers", "contact_phone", schema="pycrm")
    op.drop_column("shipping_carriers", "contact_name", schema="pycrm")
    op.drop_column("shipping_carriers", "tracking_url_template", schema="pycrm")
    op.drop_column("shipping_carriers", "api_endpoint", schema="pycrm")
    op.drop_column("shipping_carriers", "api_key", schema="pycrm")
    op.drop_column("shipping_carriers", "payment_terms", schema="pycrm")
    op.drop_column("shipping_carriers", "billing_address", schema="pycrm")
    op.drop_column("shipping_carriers", "code", schema="pycrm")
