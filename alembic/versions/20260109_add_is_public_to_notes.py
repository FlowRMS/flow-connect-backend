"""add is_public column to notes

Revision ID: add_is_public_to_notes
Revises: add_task_assignees
Create Date: 2026-01-09

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_is_public_to_notes"
down_revision: str | None = "add_task_assignees"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "notes",
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default="false"),
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_column("notes", "is_public", schema="pycrm")
