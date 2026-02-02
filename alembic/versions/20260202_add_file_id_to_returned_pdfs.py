# Add file_id to submittal_returned_pdfs for fresh presigned URL generation
# Revision ID: add_file_id_to_returned_pdfs
# Revises: fix_pdf_file_size_column
# Create Date: 2026-02-02

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_file_id_to_returned_pdfs"
down_revision: str | None = "fix_pdf_file_size_column"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add file_id column to store reference to files table
    op.add_column(
        "submittal_returned_pdfs",
        sa.Column("file_id", UUID(as_uuid=True), nullable=True),
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_column("submittal_returned_pdfs", "file_id", schema="pycrm")
