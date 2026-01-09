"""Add user_ids column to orders, quotes, invoices, and checks.

This denormalizes user ownership for faster landing page queries.
The user_ids array contains: created_by_id + all split rate user_ids.

Revision ID: add_user_ids_001
Revises: order_acknowledgements_001
Create Date: 2025-01-02

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_user_ids_001"
down_revision: str | None = "order_acknowledgements_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column(
            "user_ids",
            postgresql.ARRAY(sa.UUID()),
            nullable=False,
            server_default="{}",
        ),
        schema="pycommission",
    )

    op.add_column(
        "quotes",
        sa.Column(
            "user_ids",
            postgresql.ARRAY(sa.UUID()),
            nullable=False,
            server_default="{}",
        ),
        schema="pycrm",
    )

    op.add_column(
        "invoices",
        sa.Column(
            "user_ids",
            postgresql.ARRAY(sa.UUID()),
            nullable=False,
            server_default="{}",
        ),
        schema="pycommission",
    )

    op.add_column(
        "checks",
        sa.Column(
            "user_ids",
            postgresql.ARRAY(sa.UUID()),
            nullable=False,
            server_default="{}",
        ),
        schema="pycommission",
    )

    # Add GIN indexes for efficient array containment queries (RBAC filtering)
    op.create_index(
        "ix_orders_user_ids",
        "orders",
        ["user_ids"],
        schema="pycommission",
        postgresql_using="gin",
    )

    op.create_index(
        "ix_quotes_user_ids",
        "quotes",
        ["user_ids"],
        schema="pycrm",
        postgresql_using="gin",
    )

    op.create_index(
        "ix_invoices_user_ids",
        "invoices",
        ["user_ids"],
        schema="pycommission",
        postgresql_using="gin",
    )

    op.create_index(
        "ix_checks_user_ids",
        "checks",
        ["user_ids"],
        schema="pycommission",
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_checks_user_ids", table_name="checks", schema="pycommission")
    op.drop_index("ix_invoices_user_ids", table_name="invoices", schema="pycommission")
    op.drop_index("ix_quotes_user_ids", table_name="quotes", schema="pycrm")
    op.drop_index("ix_orders_user_ids", table_name="orders", schema="pycommission")

    op.drop_column("checks", "user_ids", schema="pycommission")
    op.drop_column("invoices", "user_ids", schema="pycommission")
    op.drop_column("quotes", "user_ids", schema="pycrm")
    op.drop_column("orders", "user_ids", schema="pycommission")
