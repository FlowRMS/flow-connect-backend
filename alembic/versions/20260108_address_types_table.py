"""create address_types table and migrate data

Revision ID: address_types_table_001
Revises: add_visible_to_users
Create Date: 2026-01-08

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "address_types_table_001"
down_revision: str | None = "add_visible_to_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "address_types",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("address_id", sa.UUID(), nullable=False),
        sa.Column("type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["address_id"],
            ["pycore.addresses.id"],
            ondelete="CASCADE",
        ),
        schema="pycore",
    )
    op.create_index(
        "ix_address_types_address_id",
        "address_types",
        ["address_id"],
        schema="pycore",
    )

    # Migrate existing data: create address_type rows from existing address_type column
    op.execute(
        """
        INSERT INTO pycore.address_types (id, address_id, type)
        SELECT gen_random_uuid(), id, address_type
        FROM pycore.addresses
        WHERE address_type IS NOT NULL
        """
    )

    # Drop the address_type column from addresses table
    op.drop_column("addresses", "address_type", schema="pycore")


def downgrade() -> None:
    # Add back the address_type column
    op.add_column(
        "addresses",
        sa.Column("address_type", sa.SmallInteger(), nullable=True, server_default="4"),
        schema="pycore",
    )

    # Migrate data back: take the first address_type for each address
    op.execute(
        """
        UPDATE pycore.addresses a
        SET address_type = (
            SELECT at.type
            FROM pycore.address_types at
            WHERE at.address_id = a.id
            LIMIT 1
        )
        """
    )

    # Set default for addresses without types
    op.execute(
        """
        UPDATE pycore.addresses
        SET address_type = 4
        WHERE address_type IS NULL
        """
    )

    # Make column non-nullable
    op.alter_column(
        "addresses",
        "address_type",
        nullable=False,
        schema="pycore",
    )

    op.drop_index(
        "ix_address_types_address_id",
        table_name="address_types",
        schema="pycore",
    )
    op.drop_table("address_types", schema="pycore")
