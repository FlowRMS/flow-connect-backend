"""adding quotes

Revision ID: b57a72ba9d00
Revises: 5a8b3c2d1e0f
Create Date: 2025-12-24 19:26:53.312502

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b57a72ba9d00"
down_revision: str | None = "5a8b3c2d1e0f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "quote_balances",
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
        schema="pycrm",
    )
    _ = op.create_table(
        "quote_lost_reasons",
        sa.Column("created_by_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["pyuser.users.id"],
        ),
        schema="pycrm",
    )
    _ = op.create_table(
        "quotes",
        sa.Column("quote_number", sa.String(length=255), nullable=False),
        sa.Column("entity_date", sa.Date(), nullable=False),
        sa.Column("sold_to_customer_id", sa.UUID(), nullable=False),
        sa.Column("bill_to_customer_id", sa.UUID(), nullable=True),
        sa.Column("published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "creation_type", sa.SmallInteger(), nullable=False, server_default="0"
        ),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column(
            "pipeline_stage", sa.SmallInteger(), nullable=False, server_default="0"
        ),
        sa.Column("payment_terms", sa.String(length=255), nullable=True),
        sa.Column("customer_ref", sa.String(length=255), nullable=True),
        sa.Column("freight_terms", sa.String(length=255), nullable=True),
        sa.Column("exp_date", sa.Date(), nullable=True),
        sa.Column("revise_date", sa.Date(), nullable=True),
        sa.Column("accept_date", sa.Date(), nullable=True),
        sa.Column("blanket", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("duplicated_from", sa.UUID(), nullable=True),
        sa.Column("version_of", sa.UUID(), nullable=True),
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
            ["pycrm.quote_balances.id"],
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
            ["sold_to_customer_id"],
            ["pycore.customers.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("balance_id"),
        sa.UniqueConstraint(
            "quote_number", "sold_to_customer_id", name="uq_quote_number_sold_to"
        ),
        schema="pycrm",
    )
    _ = op.create_table(
        "quote_inside_reps",
        sa.Column("quote_id", sa.UUID(), nullable=False),
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
            ["quote_id"],
            ["pycrm.quotes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )
    _ = op.create_table(
        "quote_details",
        sa.Column("quote_id", sa.UUID(), nullable=False),
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
        sa.Column("product_id", sa.UUID(), nullable=True),
        sa.Column("product_name_adhoc", sa.String(length=255), nullable=True),
        sa.Column("product_description_adhoc", sa.Text(), nullable=True),
        sa.Column("factory_id", sa.UUID(), nullable=True),
        sa.Column("end_user_id", sa.UUID(), nullable=True),
        sa.Column("uom_id", sa.UUID(), nullable=True),
        sa.Column(
            "division_factor",
            sa.Numeric(precision=18, scale=6),
            nullable=True,
        ),
        sa.Column("lead_time", sa.String(length=255), nullable=True),
        sa.Column("note", sa.String(length=2000), nullable=True),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("lost_reason_id", sa.UUID(), nullable=True),
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
            ["lost_reason_id"],
            ["pycrm.quote_lost_reasons.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["pycore.products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["quote_id"],
            ["pycrm.quotes.id"],
        ),
        sa.ForeignKeyConstraint(
            ["uom_id"],
            ["pycore.product_uoms.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )
    _ = op.create_table(
        "quote_split_rates",
        sa.Column("quote_detail_id", sa.UUID(), nullable=False),
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
            ["quote_detail_id"],
            ["pycrm.quote_details.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["pyuser.users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_table("quote_inside_reps", schema="pycrm")
    op.drop_table("quote_split_rates", schema="pycrm")
    op.drop_table("quote_details", schema="pycrm")
    op.drop_table("quote_lost_reasons", schema="pycrm")
    op.drop_table("quote_balances", schema="pycrm")
