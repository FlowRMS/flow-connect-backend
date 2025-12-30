"""adding addresses table

Revision ID: 6e453caa5fb9
Revises: c04c14e9ba47
Create Date: 2025-12-26 15:37:31.885776

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "6e453caa5fb9"
down_revision: str | None = "c04c14e9ba47"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "addresses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column("source_type", sa.SmallInteger(), nullable=False),
        sa.Column(
            "address_type", sa.SmallInteger(), nullable=False, server_default="4"
        ),
        sa.Column("line_1", sa.String(255), nullable=False),
        sa.Column("line_2", sa.String(255), nullable=True),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("zip_code", sa.String(20), nullable=False),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycore",
    )
    op.create_index(
        "ix_addresses_source",
        "addresses",
        ["source_type", "source_id"],
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_addresses_source",
        table_name="addresses",
        schema="pycore",
    )
    op.drop_table("addresses", schema="pycore")
