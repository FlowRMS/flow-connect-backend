"""Fix inventory_items location_id foreign key to use SET NULL on delete

Revision ID: fix_inventory_items_location_fk
Revises: add_commission_statements
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "fix_inventory_items_location_fk"
down_revision: str | None = "add_commission_statements"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Only modify if the table exists (some tenants may not have inventory module)
    if not inspector.has_table("inventory_items", schema="pywarehouse"):
        return

    # Drop existing FK constraint
    op.drop_constraint(
        "inventory_items_location_id_fkey",
        "inventory_items",
        schema="pywarehouse",
        type_="foreignkey",
    )

    # Create new FK with ON DELETE SET NULL
    op.create_foreign_key(
        "inventory_items_location_id_fkey",
        "inventory_items",
        "warehouse_locations",
        ["location_id"],
        ["id"],
        source_schema="pywarehouse",
        referent_schema="pywarehouse",
        ondelete="SET NULL",
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Only modify if the table exists
    if not inspector.has_table("inventory_items", schema="pywarehouse"):
        return

    op.drop_constraint(
        "inventory_items_location_id_fkey",
        "inventory_items",
        schema="pywarehouse",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "inventory_items_location_id_fkey",
        "inventory_items",
        "warehouse_locations",
        ["location_id"],
        ["id"],
        source_schema="pywarehouse",
        referent_schema="pywarehouse",
    )
