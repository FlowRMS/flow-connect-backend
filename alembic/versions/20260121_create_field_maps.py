"""Create field_maps and field_map_fields tables

Revision ID: 20260121_001
Revises: 20260120_001
Create Date: 2026-01-21 09:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260121_001"
down_revision: str | None = "20260120_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "field_maps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("map_type", sa.String(10), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "map_type",
            name="uq_field_maps_org_type",
        ),
        schema="connect_pos",
    )

    op.create_table(
        "field_map_fields",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_map_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("standard_field_key", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("standard_field_name", sa.String(100), nullable=False),
        sa.Column("standard_field_name_description", sa.Text(), nullable=True),
        sa.Column("organization_field_name", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("manufacturer", sa.Boolean(), nullable=True),
        sa.Column("rep", sa.Boolean(), nullable=True),
        sa.Column("linked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("preferred", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("field_type", sa.String(20), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["field_map_id"],
            ["connect_pos.field_maps.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "field_map_id",
            "standard_field_key",
            name="uq_field_map_fields_map_key",
        ),
        schema="connect_pos",
    )

    op.create_index(
        "ix_field_map_fields_field_map_id",
        "field_map_fields",
        ["field_map_id"],
        schema="connect_pos",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_field_map_fields_field_map_id",
        table_name="field_map_fields",
        schema="connect_pos",
    )
    op.drop_table("field_map_fields", schema="connect_pos")
    op.drop_table("field_maps", schema="connect_pos")
