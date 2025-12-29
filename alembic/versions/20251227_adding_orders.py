"""adding orders

Revision ID: 7a8b9c0d1e2f
Revises: 6e453caa5fb9
Create Date: 2025-12-27 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "7a8b9c0d1e2f"
down_revision: str | None = "6e453caa5fb9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "order_balances",
        sa.Column(
            "quantity",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "subtotal",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "total",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "commission",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "discount",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "discount_rate",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "commission_rate",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "commission_discount",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "commission_discount_rate",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "shipping_balance",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "cancelled_balance",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "freight_charge_balance",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )
    _ = op.create_table(
        "orders",
        sa.Column("order_number", sa.String(length=255), nullable=False),
        sa.Column("entity_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("sold_to_customer_id", sa.UUID(), nullable=False),
        sa.Column("bill_to_customer_id", sa.UUID(), nullable=True),
        sa.Column("published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "creation_type", sa.SmallInteger(), nullable=False, server_default="0"
        ),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("order_type", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column(
            "header_status", sa.SmallInteger(), nullable=False, server_default="1"
        ),
        sa.Column("factory_id", sa.UUID(), nullable=True),
        sa.Column("shipping_terms", sa.String(length=255), nullable=True),
        sa.Column("freight_terms", sa.String(length=255), nullable=True),
        sa.Column("mark_number", sa.String(length=255), nullable=True),
        sa.Column("ship_date", sa.Date(), nullable=True),
        sa.Column("projected_ship_date", sa.Date(), nullable=True),
        sa.Column("fact_so_number", sa.String(length=255), nullable=True),
        sa.Column("quote_id", sa.UUID(), nullable=True),
        sa.Column("balance_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["balance_id"],
            ["pycommission.order_balances.id"],
        ),
        sa.ForeignKeyConstraint(
            ["bill_to_customer_id"],
            ["pycore.customers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["factory_id"],
            ["pycore.factories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["quote_id"],
            ["pycrm.quotes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sold_to_customer_id"],
            ["pycore.customers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("balance_id"),
        schema="pycommission",
    )
    _ = op.create_table(
        "order_inside_reps",
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "split_rate",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["pycommission.orders.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )
    _ = op.create_table(
        "order_details",
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("item_number", sa.Integer(), nullable=False),
        sa.Column(
            "quantity",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "unit_price",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "subtotal",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "total",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "total_line_commission",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "commission_rate",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "commission",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "commission_discount_rate",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "commission_discount",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "discount_rate",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "discount",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "division_factor",
            sa.Numeric(precision=18, scale=6),
            nullable=True,
        ),
        sa.Column("product_id", sa.UUID(), nullable=True),
        sa.Column("product_name_adhoc", sa.String(length=255), nullable=True),
        sa.Column("product_description_adhoc", sa.Text(), nullable=True),
        sa.Column("factory_id", sa.UUID(), nullable=True),
        sa.Column("end_user_id", sa.UUID(), nullable=True),
        sa.Column("uom_id", sa.UUID(), nullable=True),
        sa.Column("lead_time", sa.String(length=255), nullable=True),
        sa.Column("note", sa.String(length=2000), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column(
            "freight_charge",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "shipping_balance",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "cancelled_balance",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["end_user_id"],
            ["pycore.customers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["factory_id"],
            ["pycore.factories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["pycore.products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["pycommission.orders.id"],
        ),
        sa.ForeignKeyConstraint(
            ["uom_id"],
            ["pycore.product_uoms.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )
    _ = op.create_table(
        "order_split_rates",
        sa.Column("order_detail_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "split_rate",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["order_detail_id"],
            ["pycommission.order_details.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )
    op.create_foreign_key(
        "fk_quote_details_order_id_orders",
        "quote_details",
        "orders",
        ["order_id"],
        ["id"],
        source_schema="pycrm",
        referent_schema="pycommission",
    )


def downgrade() -> None:
    op.drop_table("order_split_rates", schema="pycommission")
    op.drop_table("order_details", schema="pycommission")
    op.drop_table("order_inside_reps", schema="pycommission")
    op.drop_table("orders", schema="pycommission")
    op.drop_table("order_balances", schema="pycommission")
