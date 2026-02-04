"""add file_id to spec_sheets for /files integration

Revision ID: spec_sheet_file_id
Revises: add_commission_statements
Create Date: 2026-01-19 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "spec_sheet_file_id"
down_revision: str | None = "add_commission_statements"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)

    # Check if column already exists
    columns = [
        col["name"] for col in inspector.get_columns("spec_sheets", schema="pycrm")
    ]
    if "file_id" in columns:
        return

    # Add file_id column to spec_sheets table for /files integration
    # This allows spec sheets to appear in /files when browsing by Factory entity
    op.add_column(
        "spec_sheets",
        sa.Column(
            "file_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            index=True,
        ),
        schema="pycrm",
    )

    # Add foreign key constraint to pyfiles.files
    op.create_foreign_key(
        "fk_spec_sheets_file_id",
        "spec_sheets",
        "files",
        ["file_id"],
        ["id"],
        source_schema="pycrm",
        referent_schema="pyfiles",
        ondelete="SET NULL",
    )

    # Create index for faster lookups
    op.create_index(
        "ix_spec_sheets_file_id",
        "spec_sheets",
        ["file_id"],
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_index("ix_spec_sheets_file_id", table_name="spec_sheets", schema="pycrm")
    op.drop_constraint(
        "fk_spec_sheets_file_id", "spec_sheets", schema="pycrm", type_="foreignkey"
    )
    op.drop_column("spec_sheets", "file_id", schema="pycrm")
