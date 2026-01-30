"""add factory_per_line_item to orders

Revision ID: factory_plitem_orders
Revises: tags_core_entities
Create Date: 2026-01-27

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "factory_plitem_orders"
down_revision: str | None = "tags_core_entities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def column_exists(table: str, column: str, schema: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = :schema
            AND table_name = :table
            AND column_name = :column
        """),
        {"schema": schema, "table": table, "column": column},
    )
    return result.scalar() is not None


def constraint_exists(constraint_name: str, schema: str) -> bool:
    conn = op.get_bind()
    result = conn.execute(
        sa.text("""
            SELECT 1 FROM information_schema.table_constraints
            WHERE constraint_schema = :schema
            AND constraint_name = :constraint_name
        """),
        {"schema": schema, "constraint_name": constraint_name},
    )
    return result.scalar() is not None


def upgrade() -> None:
    if not column_exists("orders", "factory_per_line_item", "pycommission"):
        _ = op.add_column(
            "orders",
            sa.Column(
                "factory_per_line_item",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            schema="pycommission",
        )

    op.alter_column(
        "orders",
        "factory_id",
        existing_type=sa.UUID(),
        nullable=True,
        schema="pycommission",
    )

    if not column_exists("order_details", "factory_id", "pycommission"):
        _ = op.add_column(
            "order_details",
            sa.Column("factory_id", sa.UUID(), nullable=True),
            schema="pycommission",
        )

    if not constraint_exists("fk_order_details_factory_id", "pycommission"):
        op.create_foreign_key(
            "fk_order_details_factory_id",
            "order_details",
            "factories",
            ["factory_id"],
            ["id"],
            source_schema="pycommission",
            referent_schema="pycore",
        )


def downgrade() -> None:
    op.drop_constraint(
        "fk_order_details_factory_id",
        "order_details",
        schema="pycommission",
    )
    op.drop_column("order_details", "factory_id", schema="pycommission")

    # Check for NULL values before making column NOT NULL
    conn = op.get_bind()
    result = conn.execute(
        sa.text("SELECT COUNT(*) FROM pycommission.orders WHERE factory_id IS NULL")
    )
    null_count = result.scalar()
    if null_count and null_count > 0:
        raise RuntimeError(
            f"Cannot downgrade: {null_count} orders have NULL factory_id. "
            "Please update these records before downgrading."
        )

    op.alter_column(
        "orders",
        "factory_id",
        existing_type=sa.UUID(),
        nullable=False,
        schema="pycommission",
    )
    op.drop_column("orders", "factory_per_line_item", schema="pycommission")
