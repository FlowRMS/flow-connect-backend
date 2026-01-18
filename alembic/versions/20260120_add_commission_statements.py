"""add commission statements tables

Revision ID: add_commission_statements
Revises: add_territory_to_entities
Create Date: 2026-01-20

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_commission_statements"
down_revision: str | None = "add_territory_to_entities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "commission_statement_balances",
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
        sa.Column("id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )
    _ = op.create_table(
        "commission_statements",
        sa.Column("statement_number", sa.String(length=255), nullable=False),
        sa.Column("factory_id", sa.UUID(), nullable=False),
        sa.Column("entity_date", sa.Date(), nullable=False),
        sa.Column(
            "creation_type", sa.SmallInteger(), nullable=False, server_default="0"
        ),
        sa.Column("balance_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "user_ids",
            postgresql.ARRAY(sa.UUID()),
            nullable=False,
            server_default="{}",
        ),
        sa.ForeignKeyConstraint(
            ["balance_id"],
            ["pycommission.commission_statement_balances.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["factory_id"],
            ["pycore.factories.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("balance_id"),
        schema="pycommission",
    )
    _ = op.create_table(
        "commission_statement_details",
        sa.Column("statement_id", sa.UUID(), nullable=False),
        sa.Column("sold_to_customer_id", sa.UUID(), nullable=True),
        sa.Column("order_id", sa.UUID(), nullable=True),
        sa.Column("order_detail_id", sa.UUID(), nullable=True),
        sa.Column("invoice_id", sa.UUID(), nullable=True),
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
        sa.Column("uom_id", sa.UUID(), nullable=True),
        sa.Column("end_user_id", sa.UUID(), nullable=True),
        sa.Column("lead_time", sa.String(length=255), nullable=True),
        sa.Column("note", sa.String(length=2000), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["statement_id"],
            ["pycommission.commission_statements.id"],
        ),
        sa.ForeignKeyConstraint(
            ["sold_to_customer_id"],
            ["pycore.customers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["pycommission.orders.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_detail_id"],
            ["pycommission.order_details.id"],
        ),
        sa.ForeignKeyConstraint(
            ["invoice_id"],
            ["pycommission.invoices.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["pycore.products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["uom_id"],
            ["pycore.product_uoms.id"],
        ),
        sa.ForeignKeyConstraint(
            ["end_user_id"],
            ["pycore.customers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )
    _ = op.create_table(
        "commission_statement_split_rates",
        sa.Column("statement_detail_id", sa.UUID(), nullable=False),
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
            ["statement_detail_id"],
            ["pycommission.commission_statement_details.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )


def downgrade() -> None:
    op.drop_table("commission_statement_split_rates", schema="pycommission")
    op.drop_table("commission_statement_details", schema="pycommission")
    op.drop_table("commission_statements", schema="pycommission")
    op.drop_table("commission_statement_balances", schema="pycommission")
