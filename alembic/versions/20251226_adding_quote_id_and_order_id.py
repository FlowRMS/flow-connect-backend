"""adding quote_id and order id

Revision ID: c04c14e9ba47
Revises: 8a3f2c1d5e9b
Create Date: 2025-12-26 12:18:39.358115

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c04c14e9ba47"
down_revision: str | None = "8a3f2c1d5e9b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.add_column(
        "pre_opportunity_details",
        sa.Column("quote_id", sa.UUID(), nullable=True),
        schema="pycrm",
    )
    op.create_foreign_key(
        "fk_pre_opportunity_details_quote_id_quotes",
        "pre_opportunity_details",
        "quotes",
        ["quote_id"],
        ["id"],
        source_schema="pycrm",
        referent_schema="pycrm",
    )
    _ = op.add_column(
        "quote_details",
        sa.Column("order_id", sa.UUID(), nullable=True),
        schema="pycrm",
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
    pass
