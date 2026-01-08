from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "06f9eafc78e0"
down_revision: str | None = "21588c21d093"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.add_column(
        "quotes",
        sa.Column(
            "factory_per_line_item",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_column("quotes", "factory_per_line_item", schema="pycrm")
