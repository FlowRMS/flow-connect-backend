"""create spec_sheet_folders table

Revision ID: create_spec_sheet_folders
Revises: d538c52154d8
Create Date: 2026-01-19

Creates spec_sheet_folders table that maps pyfiles.folders to factories.
This allows each factory to have its own folder hierarchy for organizing spec sheets.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "create_spec_sheet_folders"
down_revision: str | None = "d538c52154d8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names(schema="pycrm")

    if "spec_sheet_folders" not in tables:
        op.create_table(
            "spec_sheet_folders",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column("factory_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column(
                "pyfiles_folder_id", postgresql.UUID(as_uuid=True), nullable=False
            ),
            sa.Column(
                "created_at",
                postgresql.TIMESTAMP(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.ForeignKeyConstraint(
                ["pyfiles_folder_id"],
                ["pyfiles.folders.id"],
                name="fk_spec_sheet_folders_pyfiles_folder",
                ondelete="CASCADE",
            ),
            sa.UniqueConstraint(
                "factory_id",
                "pyfiles_folder_id",
                name="uq_spec_sheet_folders_factory_pyfiles",
            ),
            schema="pycrm",
        )

        op.create_index(
            "idx_spec_sheet_folders_factory_id",
            "spec_sheet_folders",
            ["factory_id"],
            schema="pycrm",
        )

        op.create_index(
            "idx_spec_sheet_folders_pyfiles_folder_id",
            "spec_sheet_folders",
            ["pyfiles_folder_id"],
            schema="pycrm",
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names(schema="pycrm")

    if "spec_sheet_folders" in tables:
        op.drop_index(
            "idx_spec_sheet_folders_pyfiles_folder_id",
            table_name="spec_sheet_folders",
            schema="pycrm",
        )
        op.drop_index(
            "idx_spec_sheet_folders_factory_id",
            table_name="spec_sheet_folders",
            schema="pycrm",
        )
        op.drop_table("spec_sheet_folders", schema="pycrm")
