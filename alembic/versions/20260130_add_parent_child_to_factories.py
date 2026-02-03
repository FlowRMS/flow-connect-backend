"""add_parent_child_to_factories

Revision ID: add_factory_parent_child
Revises: commons_v3_schema_changes
Create Date: 2026-01-30 17:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_factory_parent_child"
down_revision: str | None = "commons_v3_schema_changes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add is_parent column with default value false
    op.add_column(
        "factories",
        sa.Column("is_parent", sa.Boolean(), nullable=False, server_default="false"),
        schema="pycore",
    )
    # Add parent_id column with foreign key to self
    op.add_column(
        "factories",
        sa.Column(
            "parent_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        schema="pycore",
    )
    # Add foreign key constraint
    op.create_foreign_key(
        "fk_factories_parent_id",
        "factories",
        "factories",
        ["parent_id"],
        ["id"],
        source_schema="pycore",
        referent_schema="pycore",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_factories_parent_id", "factories", schema="pycore", type_="foreignkey"
    )
    op.drop_column("factories", "parent_id", schema="pycore")
    op.drop_column("factories", "is_parent", schema="pycore")
