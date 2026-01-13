"""add buying_group_id column to customers

Revision ID: add_buying_group
Revises: add_is_public_to_notes
Create Date: 2026-01-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_buying_group"
down_revision: str | None = "add_is_public_to_notes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column(
            "buying_group_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycore.customers.id"),
            nullable=True,
        ),
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_column("customers", "buying_group_id", schema="pycore")
