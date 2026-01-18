"""Migrate fulfillment_order ship_to_address JSONB to FK

Revision ID: fulfillment_address_fk
Revises: 20260107_freight_class
Create Date: 2026-01-14

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "fulfillment_address_fk"
down_revision: str | None = "20260107_freight_class"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Step 1: Add new columns
    op.add_column(
        "fulfillment_orders",
        sa.Column("ship_to_address_id", postgresql.UUID(as_uuid=True), nullable=True),
        schema="pywarehouse",
    )
    op.add_column(
        "fulfillment_orders",
        sa.Column("ship_to_name", sa.String(255), nullable=True),
        schema="pywarehouse",
    )
    op.add_column(
        "fulfillment_orders",
        sa.Column("ship_to_phone", sa.String(50), nullable=True),
        schema="pywarehouse",
    )

    # Step 2: Create index on the new FK
    op.create_index(
        "ix_fulfillment_orders_ship_to_address_id",
        "fulfillment_orders",
        ["ship_to_address_id"],
        schema="pywarehouse",
    )

    # Step 3: Add FK constraint
    op.create_foreign_key(
        "fk_fulfillment_orders_ship_to_address",
        "fulfillment_orders",
        "addresses",
        ["ship_to_address_id"],
        ["id"],
        source_schema="pywarehouse",
        referent_schema="pycore",
    )

    # Step 4: Migrate data - Create Address records from JSONB
    # AddressSourceTypeEnum.FULFILLMENT_ORDER = 4
    op.execute(
        """
        INSERT INTO pycore.addresses (
            id, source_id, source_type, line_1, line_2, city, state, zip_code, country, is_primary, created_at
        )
        SELECT
            gen_random_uuid(),
            fo.id,
            4,
            COALESCE((fo.ship_to_address->>'street')::text, ''),
            (fo.ship_to_address->>'street_line_2')::text,
            COALESCE((fo.ship_to_address->>'city')::text, ''),
            (fo.ship_to_address->>'state')::text,
            (fo.ship_to_address->>'postal_code')::text,
            COALESCE((fo.ship_to_address->>'country')::text, ''),
            true,
            fo.created_at
        FROM pywarehouse.fulfillment_orders fo
        WHERE fo.ship_to_address IS NOT NULL
        """
    )

    # Step 5: Update fulfillment_orders with the new address IDs and extract name/phone
    op.execute(
        """
        UPDATE pywarehouse.fulfillment_orders fo
        SET
            ship_to_address_id = a.id,
            ship_to_name = (fo.ship_to_address->>'name')::text,
            ship_to_phone = (fo.ship_to_address->>'phone')::text
        FROM pycore.addresses a
        WHERE a.source_id = fo.id
          AND a.source_type = 4
        """
    )

    # Step 6: Drop the JSONB column
    op.drop_column("fulfillment_orders", "ship_to_address", schema="pywarehouse")


def downgrade() -> None:
    # Step 1: Re-add the JSONB column
    op.add_column(
        "fulfillment_orders",
        sa.Column("ship_to_address", postgresql.JSONB(), nullable=True),
        schema="pywarehouse",
    )

    # Step 2: Migrate data back to JSONB
    op.execute(
        """
        UPDATE pywarehouse.fulfillment_orders fo
        SET ship_to_address = jsonb_build_object(
            'name', fo.ship_to_name,
            'street', a.line_1,
            'street_line_2', a.line_2,
            'city', a.city,
            'state', a.state,
            'postal_code', a.zip_code,
            'country', a.country,
            'phone', fo.ship_to_phone
        )
        FROM pycore.addresses a
        WHERE a.id = fo.ship_to_address_id
        """
    )

    # Step 3: Delete the address records we created
    op.execute(
        """
        DELETE FROM pycore.addresses
        WHERE source_type = 4
        """
    )

    # Step 4: Drop FK constraint
    op.drop_constraint(
        "fk_fulfillment_orders_ship_to_address",
        "fulfillment_orders",
        schema="pywarehouse",
    )

    # Step 5: Drop index
    op.drop_index(
        "ix_fulfillment_orders_ship_to_address_id",
        table_name="fulfillment_orders",
        schema="pywarehouse",
    )

    # Step 6: Drop new columns
    op.drop_column("fulfillment_orders", "ship_to_phone", schema="pywarehouse")
    op.drop_column("fulfillment_orders", "ship_to_name", schema="pywarehouse")
    op.drop_column("fulfillment_orders", "ship_to_address_id", schema="pywarehouse")
