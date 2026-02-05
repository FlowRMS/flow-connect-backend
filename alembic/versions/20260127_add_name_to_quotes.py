"""add name column to quotes

Revision ID: add_name_to_quotes
Revises: preopp_sold_to_nullable
Create Date: 2026-01-27 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_name_to_quotes"
down_revision: str | None = "preopp_sold_to_nullable"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("quotes", schema="pycrm")]

    if "name" not in columns:
        op.add_column(
            "quotes",
            sa.Column("name", sa.String(255), nullable=True),
            schema="pycrm",
        )


def downgrade() -> None:
    op.drop_column("quotes", "name", schema="pycrm")
