"""create territory_split_rates table

Revision ID: create_territory_split_rates
Revises: create_territories
Create Date: 2026-01-17

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "create_territory_split_rates"
down_revision: str | None = "create_territories"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "territory_split_rates",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "territory_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycore.territories.id"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyuser.users.id"),
            nullable=False,
        ),
        sa.Column("split_rate", sa.Numeric(18, 6), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="pycore",
    )
    op.create_index(
        "ix_territory_split_rates_territory_id",
        "territory_split_rates",
        ["territory_id"],
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_territory_split_rates_territory_id",
        table_name="territory_split_rates",
        schema="pycore",
    )
    op.drop_table("territory_split_rates", schema="pycore")
