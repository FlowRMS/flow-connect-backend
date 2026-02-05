"""add role_detail to contacts

Revision ID: add_role_detail_contacts
Revises: tags_core_entities
Create Date: 2026-02-02 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_role_detail_contacts"
down_revision: str | None = "tags_core_entities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    columns = [col["name"] for col in inspector.get_columns("contacts", schema="pycrm")]

    if "role_detail" not in columns:
        op.add_column(
            "contacts",
            sa.Column("role_detail", sa.String(1000), nullable=True),
            schema="pycrm",
        )


def downgrade() -> None:
    op.drop_column("contacts", "role_detail", schema="pycrm")
