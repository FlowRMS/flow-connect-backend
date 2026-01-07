"""adding factory_per_line_item to quotes

Revision ID: 4d002e14da98
Revises: add_user_ids_001
Create Date: 2026-01-03 19:47:16.582595

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "factory_plitem_quotes"
down_revision: str | None = "add_user_ids_001"
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
