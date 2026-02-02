"""add role_detail to contacts

Revision ID: add_role_detail_contacts
Revises: 7702478b47b2
Create Date: 2026-02-02 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_role_detail_contacts"
down_revision: str | None = "7702478b47b2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "contacts", sa.Column("role_detail", sa.String(1000), nullable=True), schema="pycrm"
    )


def downgrade() -> None:
    op.drop_column("contacts", "role_detail", schema="pycrm")
