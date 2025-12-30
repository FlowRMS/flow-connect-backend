"""adding commission remaining

Revision ID: 62e4315e9e63
Revises: 983952e7b210
Create Date: 2025-12-29 23:13:12.379014

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "62e4315e9e63"
down_revision: str | None = "983952e7b210"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Invoice balances table
    _ = op.create_table(
        "invoice_balances",
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
            "paid_balance",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )

    # Invoices table
    _ = op.create_table(
        "invoices",
        sa.Column("invoice_number", sa.String(length=255), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("entity_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("published", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("locked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "creation_type", sa.SmallInteger(), nullable=False, server_default="1"
        ),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
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
            ["pycommission.invoice_balances.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["pycommission.orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("balance_id"),
        schema="pycommission",
    )

    op.create_unique_constraint(
        "uq_order_invoice_number",
        "invoices",
        ["order_id", "invoice_number"],
        schema="pycommission",
    )

    # Invoice details table
    _ = op.create_table(
        "invoice_details",
        sa.Column("invoice_id", sa.UUID(), nullable=False),
        sa.Column("order_detail_id", sa.UUID(), nullable=False),
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
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column(
            "invoiced_balance",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["invoice_id"],
            ["pycommission.invoices.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_detail_id"],
            ["pycommission.order_details.id"],
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

    # Credit balances table
    _ = op.create_table(
        "credit_balances",
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
        sa.Column("id", sa.UUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )

    # Credits table
    _ = op.create_table(
        "credits",
        sa.Column("credit_number", sa.String(length=255), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("entity_date", sa.Date(), nullable=False),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column("locked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "creation_type", sa.SmallInteger(), nullable=False, server_default="1"
        ),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("credit_type", sa.SmallInteger(), nullable=False, server_default="5"),
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
            ["pycommission.credit_balances.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["pycommission.orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("balance_id"),
        schema="pycommission",
    )

    op.create_unique_constraint(
        "uq_order_credit_number",
        "credits",
        ["order_id", "credit_number"],
        schema="pycommission",
    )

    # Credit details table
    _ = op.create_table(
        "credit_details",
        sa.Column("credit_id", sa.UUID(), nullable=False),
        sa.Column("order_detail_id", sa.UUID(), nullable=True),
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
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["credit_id"],
            ["pycommission.credits.id"],
        ),
        sa.ForeignKeyConstraint(
            ["order_detail_id"],
            ["pycommission.order_details.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )

    # Checks table
    _ = op.create_table(
        "checks",
        sa.Column("check_number", sa.String(length=255), nullable=False),
        sa.Column("entity_date", sa.Date(), nullable=False),
        sa.Column("post_date", sa.Date(), nullable=True),
        sa.Column("commission_month", sa.Date(), nullable=True),
        sa.Column(
            "entered_commission_amount",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column("factory_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column(
            "creation_type", sa.SmallInteger(), nullable=False, server_default="1"
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["factory_id"],
            ["pycore.factories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )

    # Adjustments table
    _ = op.create_table(
        "adjustments",
        sa.Column("factory_id", sa.UUID(), nullable=False),
        sa.Column("adjustment_number", sa.String(length=255), nullable=False),
        sa.Column("entity_date", sa.Date(), nullable=False),
        sa.Column("locked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("customer_id", sa.UUID(), nullable=True),
        sa.Column(
            "amount",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column(
            "creation_type", sa.SmallInteger(), nullable=False, server_default="1"
        ),
        sa.Column(
            "allocation_method", sa.SmallInteger(), nullable=False, server_default="1"
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["factory_id"],
            ["pycore.factories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["customer_id"],
            ["pycore.customers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )

    # Adjustment split rates table
    _ = op.create_table(
        "adjustment_split_rates",
        sa.Column("adjustment_id", sa.UUID(), nullable=False),
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
            ["adjustment_id"],
            ["pycommission.adjustments.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )

    # Check details table
    _ = op.create_table(
        "check_details",
        sa.Column("check_id", sa.UUID(), nullable=False),
        sa.Column("invoice_id", sa.UUID(), nullable=True),
        sa.Column("adjustment_id", sa.UUID(), nullable=True),
        sa.Column("credit_id", sa.UUID(), nullable=True),
        sa.Column(
            "applied_amount",
            sa.Numeric(precision=18, scale=6),
            nullable=False,
            server_default="0",
        ),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["check_id"],
            ["pycommission.checks.id"],
        ),
        sa.ForeignKeyConstraint(
            ["invoice_id"],
            ["pycommission.invoices.id"],
        ),
        sa.ForeignKeyConstraint(
            ["adjustment_id"],
            ["pycommission.adjustments.id"],
        ),
        sa.ForeignKeyConstraint(
            ["credit_id"],
            ["pycommission.credits.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycommission",
    )

    op.add_column(
        "quotes",
        sa.Column(
            "inside_per_line_item",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        schema="pycrm",
    )
    op.add_column(
        "quotes",
        sa.Column(
            "outside_per_line_item",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        schema="pycrm",
    )
    op.add_column(
        "quotes",
        sa.Column(
            "end_user_per_line_item",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        schema="pycrm",
    )

    op.add_column(
        "orders",
        sa.Column(
            "inside_per_line_item",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        schema="pycommission",
    )
    op.add_column(
        "orders",
        sa.Column(
            "outside_per_line_item",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        schema="pycommission",
    )
    op.add_column(
        "orders",
        sa.Column(
            "end_user_per_line_item",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        schema="pycommission",
    )


def downgrade() -> None:
    # Drop foreign keys first
    op.drop_column("orders", "end_user_per_line_item", schema="pycommission")
    op.drop_column("orders", "outside_per_line_item", schema="pycommission")
    op.drop_column("orders", "inside_per_line_item", schema="pycommission")
    op.drop_column("orders", "job_id", schema="pycommission")

    # Drop new columns from quotes
    op.drop_column("quotes", "end_user_per_line_item", schema="pycrm")
    op.drop_column("quotes", "outside_per_line_item", schema="pycrm")
    op.drop_column("quotes", "inside_per_line_item", schema="pycrm")
    op.drop_column("quotes", "job_id", schema="pycrm")
    op.drop_column("quotes", "factory_id", schema="pycrm")

    # Drop tables in reverse order
    op.drop_table("check_details", schema="pycommission")
    op.drop_table("adjustment_split_rates", schema="pycommission")
    op.drop_table("adjustments", schema="pycommission")
    op.drop_table("checks", schema="pycommission")
    op.drop_table("credit_details", schema="pycommission")
    op.drop_table("credits", schema="pycommission")
    op.drop_table("credit_balances", schema="pycommission")
    op.drop_table("invoice_details", schema="pycommission")
    op.drop_table("invoices", schema="pycommission")
    op.drop_table("invoice_balances", schema="pycommission")
