# drop folder_path, ensure pyfiles_folder_id on spec_sheet_folders
# Revision ID: drop_spec_sheet_folder_path
# Revises: 96d32cf858d0
# Create Date: 2026-01-20
# Replaces folder_path (varchar) with pyfiles_folder_id (UUID FK to pyfiles.folders).
# Table has no data so this is safe.

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "drop_spec_sheet_folder_path"
down_revision: str | None = "96d32cf858d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names(schema="pycrm")

    if "spec_sheet_folders" not in tables:
        return

    columns = [
        c["name"] for c in inspector.get_columns("spec_sheet_folders", schema="pycrm")
    ]

    # If folder_path exists, drop it
    if "folder_path" in columns:
        op.drop_column("spec_sheet_folders", "folder_path", schema="pycrm")

    # If pyfiles_folder_id doesn't exist, add it with FK and indexes
    if "pyfiles_folder_id" not in columns:
        op.add_column(
            "spec_sheet_folders",
            sa.Column(
                "pyfiles_folder_id", postgresql.UUID(as_uuid=True), nullable=False
            ),
            schema="pycrm",
        )
        op.create_foreign_key(
            "fk_spec_sheet_folders_pyfiles_folder",
            "spec_sheet_folders",
            "folders",
            ["pyfiles_folder_id"],
            ["id"],
            source_schema="pycrm",
            referent_schema="pyfiles",
            ondelete="CASCADE",
        )
        op.create_index(
            "idx_spec_sheet_folders_pyfiles_folder_id",
            "spec_sheet_folders",
            ["pyfiles_folder_id"],
            schema="pycrm",
        )
        op.create_unique_constraint(
            "uq_folder_factory_pyfiles",
            "spec_sheet_folders",
            ["factory_id", "pyfiles_folder_id"],
            schema="pycrm",
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names(schema="pycrm")

    if "spec_sheet_folders" not in tables:
        return

    columns = [
        c["name"] for c in inspector.get_columns("spec_sheet_folders", schema="pycrm")
    ]

    if "pyfiles_folder_id" in columns:
        op.drop_constraint(
            "uq_folder_factory_pyfiles",
            "spec_sheet_folders",
            schema="pycrm",
        )
        op.drop_index(
            "idx_spec_sheet_folders_pyfiles_folder_id",
            table_name="spec_sheet_folders",
            schema="pycrm",
        )
        op.drop_constraint(
            "fk_spec_sheet_folders_pyfiles_folder",
            "spec_sheet_folders",
            schema="pycrm",
        )
        op.drop_column("spec_sheet_folders", "pyfiles_folder_id", schema="pycrm")

    if "folder_path" not in columns:
        op.add_column(
            "spec_sheet_folders",
            sa.Column("folder_path", sa.String(), nullable=False),
            schema="pycrm",
        )
