"""adding external id to contacts

Revision ID: e9cbe792b9d3
Revises: d827079a2904
Create Date: 2026-01-20 15:15:54.410286

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e9cbe792b9d3"
down_revision: str | None = "d827079a2904"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "contacts", sa.Column("external_id", sa.String(), nullable=True), schema="pycrm"
    )


def downgrade() -> None:
    op.drop_column("contacts", "external_id", schema="pycrm")
