# add pdf_file_size_bytes to submittal_revisions
# Revision ID: add_pdf_file_size_to_revisions
# Revises: 2adbedfe0eff
# Create Date: 2026-01-21

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_pdf_file_size_to_revisions"
down_revision: str | None = "2adbedfe0eff"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "submittal_revisions",
        sa.Column("pdf_file_size_bytes", sa.BigInteger(), nullable=True),
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_column("submittal_revisions", "pdf_file_size_bytes", schema="pycrm")
