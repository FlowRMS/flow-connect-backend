from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c04c14e9ba47"
down_revision: str | None = "6b9c4d3e2f1a"
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


def downgrade() -> None:
    pass
