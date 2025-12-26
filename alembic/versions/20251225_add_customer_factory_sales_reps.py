"""add customer factory sales reps table

Revision ID: 6b9c4d3e2f1a
Revises: 5a8b3c2d1e0f
Create Date: 2025-12-25 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "6b9c4d3e2f1a"
down_revision: str | None = "5a8b3c2d1e0f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "customer_factory_sales_reps",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("factory_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("rate", sa.Numeric(18, 6), nullable=False, server_default="0"),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["pycore.customers.id"],
            name="fk_customer_factory_sales_reps_customer_id",
        ),
        sa.ForeignKeyConstraint(
            ["factory_id"],
            ["pycore.factories.id"],
            name="fk_customer_factory_sales_reps_factory_id",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["pycore.users.id"],
            name="fk_customer_factory_sales_reps_user_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "customer_id",
            "factory_id",
            "user_id",
            name="uq_customer_factory_user",
        ),
        schema="pycore",
    )
    op.create_index(
        "ix_customer_factory_sales_reps_customer_factory",
        "customer_factory_sales_reps",
        ["customer_id", "factory_id"],
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_customer_factory_sales_reps_customer_factory",
        table_name="customer_factory_sales_reps",
        schema="pycore",
    )
    op.drop_table("customer_factory_sales_reps", schema="pycore")
