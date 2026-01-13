"""add visible column to users

Revision ID: add_visible_to_users
Revises: location_quantity_decimal_001
Create Date: 2026-01-08

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_visible_to_users"
down_revision: str | None = "location_quantity_decimal_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("visible", sa.Boolean(), nullable=True, server_default="true"),
        schema="pyuser",
    )


def downgrade() -> None:
    op.drop_column("users", "visible", schema="pyuser")
