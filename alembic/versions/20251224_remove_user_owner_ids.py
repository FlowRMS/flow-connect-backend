"""remove user_owner_ids columns

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-24

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_column("quote_lost_reasons", "user_owner_ids", schema="pycrm")
    op.drop_column("factories", "user_owner_ids", schema="pycore")
    op.drop_column("checks", "user_owner_ids", schema="pycommission")
    op.drop_column("check_details", "user_owner_ids", schema="pycommission")
    op.drop_column("quotes", "user_owner_ids", schema="pycrm")
    op.drop_column("orders", "user_owner_ids", schema="pycommission")
    op.drop_column("products", "user_owner_ids", schema="pycore")
    op.drop_column("invoices", "user_owner_ids", schema="pycommission")


def downgrade() -> None:
    op.add_column(
        "invoices",
        sa.Column("user_owner_ids", postgresql.ARRAY(sa.UUID()), nullable=False),
        schema="pycommission",
    )
    op.add_column(
        "products",
        sa.Column("user_owner_ids", postgresql.ARRAY(sa.UUID()), nullable=False),
        schema="pycore",
    )
    op.add_column(
        "orders",
        sa.Column("user_owner_ids", postgresql.ARRAY(sa.UUID()), nullable=False),
        schema="pycommission",
    )
    op.add_column(
        "quotes",
        sa.Column("user_owner_ids", postgresql.ARRAY(sa.UUID()), nullable=False),
        schema="pycrm",
    )
    op.add_column(
        "check_details",
        sa.Column("user_owner_ids", postgresql.ARRAY(sa.UUID()), nullable=False),
        schema="pycommission",
    )
    op.add_column(
        "checks",
        sa.Column("user_owner_ids", postgresql.ARRAY(sa.UUID()), nullable=False),
        schema="pycommission",
    )
    op.add_column(
        "factories",
        sa.Column("user_owner_ids", postgresql.ARRAY(sa.UUID()), nullable=False),
        schema="pycore",
    )
    op.add_column(
        "quote_lost_reasons",
        sa.Column("user_owner_ids", postgresql.ARRAY(sa.UUID()), nullable=False),
        schema="pycrm",
    )
