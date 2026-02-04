"""add factory_customer_references table

Revision ID: add_factory_customer_references
Revises: undo_null_sold_to
Create Date: 2026-02-03 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision: str = "add_factory_customer_references"
down_revision: str | None = "undo_null_sold_to"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names(schema="pycore")

    if "factory_customer_references" in tables:
        return

    _ = op.create_table(
        "factory_customer_references",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("factory_id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("reference_number", sa.String(255), nullable=False),
        sa.Column("address_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["factory_id"],
            ["pycore.factories.id"],
            name="fk_factory_customer_references_factory_id",
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["pycore.customers.id"],
            name="fk_factory_customer_references_customer_id",
        ),
        sa.ForeignKeyConstraint(
            ["address_id"],
            ["pycore.addresses.id"],
            name="fk_factory_customer_references_address_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "factory_id",
            "customer_id",
            name="uq_factory_customer_reference",
        ),
        schema="pycore",
    )
    op.create_index(
        "ix_factory_customer_references_factory_id",
        "factory_customer_references",
        ["factory_id"],
        schema="pycore",
    )
    op.create_index(
        "ix_factory_customer_references_customer_id",
        "factory_customer_references",
        ["customer_id"],
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_factory_customer_references_customer_id",
        table_name="factory_customer_references",
        schema="pycore",
    )
    op.drop_index(
        "ix_factory_customer_references_factory_id",
        table_name="factory_customer_references",
        schema="pycore",
    )
    op.drop_table("factory_customer_references", schema="pycore")
