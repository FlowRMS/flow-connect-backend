"""create_folders_table

Revision ID: create_folders_001
Revises: highlight_tags_001
Create Date: 2026-01-15 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "create_folders_001"
down_revision: str | None = "highlight_tags_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create folders table for organizing spec sheets."""
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names(schema="pycrm")

    if "spec_sheet_folders" not in tables:
        _ = op.create_table(
            "spec_sheet_folders",
            sa.Column(
                "id",
                postgresql.UUID(as_uuid=True),
                primary_key=True,
                server_default=sa.text("gen_random_uuid()"),
            ),
            sa.Column("factory_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("folder_path", sa.String(500), nullable=False),
            sa.Column(
                "created_at",
                postgresql.TIMESTAMP(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
            sa.UniqueConstraint(
                "factory_id", "folder_path", name="uq_folder_factory_path"
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
            "idx_spec_sheet_folders_folder_path",
            "spec_sheet_folders",
            ["folder_path"],
            schema="pycrm",
        )


def downgrade() -> None:
    """Drop spec_sheet_folders table."""
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names(schema="pycrm")

    if "spec_sheet_folders" in tables:
        op.drop_index(
            "idx_spec_sheet_folders_folder_path",
            table_name="spec_sheet_folders",
            schema="pycrm",
        )
        op.drop_index(
            "idx_spec_sheet_folders_factory_id",
            table_name="spec_sheet_folders",
            schema="pycrm",
        )
        op.drop_table("spec_sheet_folders", schema="pycrm")
