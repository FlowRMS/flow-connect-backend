"""create territory_managers table

Revision ID: create_territory_managers
Revises: create_territory_split_rates
Create Date: 2026-01-18

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "create_territory_managers"
down_revision: str | None = "create_territory_split_rates"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "territory_managers",
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
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("territory_id", "user_id", name="uq_territory_manager"),
        schema="pycore",
    )
    op.create_index(
        "ix_territory_managers_user_id",
        "territory_managers",
        ["user_id"],
        schema="pycore",
    )
    op.create_index(
        "ix_territory_managers_territory_id",
        "territory_managers",
        ["territory_id"],
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_territory_managers_territory_id",
        table_name="territory_managers",
        schema="pycore",
    )
    op.drop_index(
        "ix_territory_managers_user_id",
        table_name="territory_managers",
        schema="pycore",
    )
    op.drop_table("territory_managers", schema="pycore")
