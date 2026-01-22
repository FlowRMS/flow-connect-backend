"""add aliases table

Revision ID: add_aliases_table
Revises: add_commission_statements
Create Date: 2026-01-21

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_aliases_table"
down_revision: str | None = "add_report_sharing_table"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "aliases",
        sa.Column(
            "id", postgresql.UUID(as_uuid=True), nullable=False, primary_key=True
        ),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.SmallInteger(), nullable=False),
        sa.Column("sub_type", sa.SmallInteger(), nullable=True),
        sa.Column("alias", sa.String, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycore",
    )
    op.create_index(
        "ix_aliases_entity_id",
        "aliases",
        ["entity_id"],
        schema="pycore",
    )
    op.create_index(
        "ix_aliases_entity_type",
        "aliases",
        ["entity_type"],
        schema="pycore",
    )
    op.create_index(
        "ix_aliases_alias",
        "aliases",
        ["alias"],
        schema="pycore",
    )
    op.create_index(
        "ix_aliases_alias_trgm",
        "aliases",
        ["alias"],
        schema="pycore",
        postgresql_using="gin",
        postgresql_ops={"alias": "gin_trgm_ops"},
    )


def downgrade() -> None:
    op.drop_index("ix_aliases_alias_trgm", table_name="aliases", schema="pycore")
    op.drop_index("ix_aliases_alias", table_name="aliases", schema="pycore")
    op.drop_index("ix_aliases_entity_type", table_name="aliases", schema="pycore")
    op.drop_index("ix_aliases_entity_id", table_name="aliases", schema="pycore")
    op.drop_table("aliases", schema="pycore")
