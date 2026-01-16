"""create territories table

Revision ID: create_territories
Revises: add_company_types
Create Date: 2026-01-16

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "create_territories"
down_revision: str | None = "add_company_types"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "territories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("territory_type", sa.Integer(), nullable=False),
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycore.territories.id"),
            nullable=True,
        ),
        sa.Column(
            "zip_codes",
            postgresql.ARRAY(sa.String(10)),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "county_codes",
            postgresql.ARRAY(sa.String(10)),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "city_names",
            postgresql.ARRAY(sa.String(100)),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "state_codes",
            postgresql.ARRAY(sa.String(5)),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="pycore",
    )
    op.create_index("ix_territories_code", "territories", ["code"], schema="pycore")
    op.create_index(
        "ix_territories_territory_type",
        "territories",
        ["territory_type"],
        schema="pycore",
    )
    op.create_index(
        "ix_territories_parent_id", "territories", ["parent_id"], schema="pycore"
    )


def downgrade() -> None:
    op.drop_index("ix_territories_parent_id", table_name="territories", schema="pycore")
    op.drop_index(
        "ix_territories_territory_type", table_name="territories", schema="pycore"
    )
    op.drop_index("ix_territories_code", table_name="territories", schema="pycore")
    op.drop_table("territories", schema="pycore")
