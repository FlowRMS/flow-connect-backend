"""adding tags to customers, factories, and products

Revision ID: 33e97afea54b
Revises: add_custom_instructions
Create Date: 2026-01-24 09:05:20.267423

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "tags_core_entities"
down_revision: str | None = "add_custom_instructions"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column("tags", sa.ARRAY(sa.String), nullable=True),
        schema="pycore",
    )
    op.add_column(
        "factories",
        sa.Column("tags", sa.ARRAY(sa.String), nullable=True),
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_column("customers", "tags", schema="pycore")
    op.drop_column("factories", "tags", schema="pycore")
