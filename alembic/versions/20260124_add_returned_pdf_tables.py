# add returned pdf tables
# Revision ID: add_returned_pdf_tables
# Revises: tags_core_entities
# Create Date: 2026-01-24
# Stub migration to maintain chain compatibility with existing database state.

from collections.abc import Sequence

from alembic import op

revision: str = "add_returned_pdf_tables"
down_revision: str | None = "tags_core_entities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
