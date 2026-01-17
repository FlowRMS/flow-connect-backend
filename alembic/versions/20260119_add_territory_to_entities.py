"""add territory_id to customers and companies

Revision ID: add_territory_to_entities
Revises: create_territory_managers
Create Date: 2026-01-19

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_territory_to_entities"
down_revision: str | None = "create_territory_managers"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "customers",
        sa.Column(
            "territory_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycore.territories.id"),
            nullable=True,
        ),
        schema="pycore",
    )
    op.create_index(
        "ix_customers_territory_id",
        "customers",
        ["territory_id"],
        schema="pycore",
    )

    op.add_column(
        "companies",
        sa.Column(
            "territory_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycore.territories.id"),
            nullable=True,
        ),
        schema="pycrm",
    )
    op.create_index(
        "ix_companies_territory_id",
        "companies",
        ["territory_id"],
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_index("ix_companies_territory_id", table_name="companies", schema="pycrm")
    op.drop_column("companies", "territory_id", schema="pycrm")

    op.drop_index("ix_customers_territory_id", table_name="customers", schema="pycore")
    op.drop_column("customers", "territory_id", schema="pycore")
