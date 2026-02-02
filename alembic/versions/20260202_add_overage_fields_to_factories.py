"""add overage fields to factories

Revision ID: add_overage_fields
Revises: add_factory_parent_child
Create Date: 2026-02-02

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_overage_fields"
down_revision: str | None = "add_factory_parent_child"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "factories",
        sa.Column("overage_allowed", sa.Boolean(), nullable=False, server_default="false"),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column("overage_type", sa.SmallInteger(), nullable=False, server_default="0"),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column("rep_overage_share", sa.Numeric(5, 2), nullable=False, server_default="100.00"),
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_column("factories", "rep_overage_share", schema="pycore")
    op.drop_column("factories", "overage_type", schema="pycore")
    op.drop_column("factories", "overage_allowed", schema="pycore")
