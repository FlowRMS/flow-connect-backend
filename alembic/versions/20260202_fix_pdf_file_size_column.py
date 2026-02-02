# Fix missing pdf_file_size_bytes column in submittal_revisions
# Revision ID: fix_pdf_file_size_column
# Revises: 5630cc7582d0
# Create Date: 2026-02-02

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fix_pdf_file_size_column"
down_revision: str | None = "5630cc7582d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add column if it doesn't exist (safe to run multiple times)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_schema = 'pycrm'
                AND table_name = 'submittal_revisions'
                AND column_name = 'pdf_file_size_bytes'
            ) THEN
                ALTER TABLE pycrm.submittal_revisions
                ADD COLUMN pdf_file_size_bytes BIGINT;
            END IF;
        END $$;
    """)


def downgrade() -> None:
    op.drop_column("submittal_revisions", "pdf_file_size_bytes", schema="pycrm")
