"""Add direction field to field_maps

Revision ID: 20260130_002
Revises: 20260130_001
Create Date: 2026-01-30 16:15:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260130_002"
down_revision: str | None = "20260130_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "field_maps",
        sa.Column("direction", sa.String(10), nullable=False, server_default="send"),
        schema="connect_pos",
    )

    op.drop_constraint(
        "uq_field_maps_org_type",
        "field_maps",
        schema="connect_pos",
    )

    op.create_unique_constraint(
        "uq_field_maps_org_type_direction",
        "field_maps",
        ["organization_id", "map_type", "direction"],
        schema="connect_pos",
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_field_maps_org_type_direction",
        "field_maps",
        schema="connect_pos",
    )

    op.create_unique_constraint(
        "uq_field_maps_org_type",
        "field_maps",
        ["organization_id", "map_type"],
        schema="connect_pos",
    )

    op.drop_column("field_maps", "direction", schema="connect_pos")
