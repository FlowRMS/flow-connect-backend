"""add_core_tables

Revision ID: 4d5e6f7g8h9i
Revises: 4d5e6f7g8h9i
Create Date: 2025-12-13 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "add_core_tables"
down_revision: str | None = "4d5e6f7g8h9i"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create users table first (referenced by other tables)
    _ = op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(255), nullable=False),
        sa.Column("last_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("auth_provider_id", sa.String(), nullable=False),
        sa.Column("inside", sa.Boolean(), nullable=True),
        sa.Column("outside", sa.Boolean(), nullable=True),
        sa.Column("supervisor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["supervisor_id"], ["users.id"]),
        sa.UniqueConstraint("email", name="uix_users_email"),
        sa.UniqueConstraint("username", name="uix_users_username"),
        sa.UniqueConstraint("auth_provider_id", name="uix_users_keycloak_id"),
    )

    _ = op.create_table(
        "factories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("account_number", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("external_terms", sa.String(), nullable=True),
        sa.Column("additional_information", sa.Text(), nullable=True),
        sa.Column("freight_terms", sa.String(), nullable=True),
        sa.Column(
            "freight_discount_type", sa.Integer(), nullable=False, server_default="1"
        ),
        sa.Column("lead_time", sa.String(), nullable=True),
        sa.Column("payment_terms", sa.String(), nullable=True),
        sa.Column("commission_rate", sa.Numeric(), nullable=True),
        sa.Column("commission_discount_rate", sa.Numeric(), nullable=True),
        sa.Column("overall_discount_rate", sa.Numeric(), nullable=True),
        sa.Column("logo_url", sa.String(), nullable=True),
        sa.Column("inside_rep_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("external_payment_terms", sa.String(), nullable=True),
        sa.Column("commission_policy", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "direct_commission_allowed",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["inside_rep_id"], ["users.id"]),
        sa.UniqueConstraint("title", name="uix_factory_title"),
    )

    _ = op.create_table(
        "customers",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("company_name", sa.String(), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_parent", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("contact_email", sa.String(), nullable=True),
        sa.Column("contact_number", sa.String(), nullable=True),
        sa.Column("customer_branch_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("customer_territory_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("logo_url", sa.String(), nullable=True),
        sa.Column("inside_rep_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["inside_rep_id"], ["users.id"]),
        sa.UniqueConstraint("company_name", name="uix_company_name"),
    )

    # Create product_uoms table
    _ = op.create_table(
        "product_uoms",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("multiply", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("multiply_by", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.UniqueConstraint("title", name="uix_product_uom_title"),
    )

    _ = op.create_table(
        "product_categories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("factory_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("commission_rate", sa.Numeric(), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["factory_id"], ["factories.id"]),
        sa.UniqueConstraint("title", "factory_id", name="uix_title_factory_id"),
    )

    # Create products table
    _ = op.create_table(
        "products",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("factory_part_number", sa.String(), nullable=False),
        sa.Column("unit_price", sa.Numeric(), nullable=False),
        sa.Column("default_commission_rate", sa.Numeric(), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("approval_needed", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("factory_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_uom_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("lead_time", sa.String(), nullable=True),
        sa.Column("min_order_qty", sa.Integer(), nullable=True),
        sa.Column("commission_discount_rate", sa.Numeric(), nullable=True),
        sa.Column("overall_discount_rate", sa.Numeric(), nullable=True),
        sa.Column("cost", sa.Numeric(), nullable=True),
        sa.Column("individual_upc", sa.String(), nullable=True),
        sa.Column("approval_comments", sa.Text(), nullable=True),
        sa.Column("logo_url", sa.String(), nullable=True),
        sa.Column("sales_model", sa.String(), nullable=True),
        sa.Column("payout_type", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["factory_id"], ["factories.id"]),
        sa.ForeignKeyConstraint(["product_category_id"], ["product_categories.id"]),
        sa.ForeignKeyConstraint(["product_uom_id"], ["product_uoms.id"]),
        sa.UniqueConstraint(
            "factory_part_number", "factory_id", name="uix_factory_part_number_factory_id"
        ),
    )


def downgrade() -> None:
    op.drop_table("products")
    op.drop_table("product_categories")
    op.drop_table("product_uoms")
    op.drop_table("customers")
    op.drop_table("factories")
    op.drop_table("users")
