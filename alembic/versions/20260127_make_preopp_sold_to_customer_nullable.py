"""make pre_opportunities sold_to_customer_id nullable

Revision ID: preopp_sold_to_nullable
Revises: tags_core_entities
Create Date: 2026-01-27 09:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "preopp_sold_to_nullable"
down_revision: str | None = "factory_plitem_orders"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "pre_opportunities",
        "sold_to_customer_id",
        existing_type=sa.UUID(),
        nullable=True,
        schema="pycrm",
    )


def downgrade() -> None:
    op.execute("""
        UPDATE pycrm.pre_opportunities
        SET sold_to_customer_id = (SELECT id FROM pycore.customers LIMIT 1)
        WHERE sold_to_customer_id IS NULL
    """)
    op.alter_column(
        "pre_opportunities",
        "sold_to_customer_id",
        existing_type=sa.UUID(),
        nullable=False,
        schema="pycrm",
    )
