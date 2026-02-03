"""add_cascade_delete_spec_sheet_highlights

Revision ID: cascade_del_highlights
Revises: 96d32cf858d0
Create Date: 2026-01-19 18:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cascade_del_highlights"
down_revision: str | None = "96d32cf858d0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. spec_sheet_highlight_versions -> spec_sheets CASCADE
    op.drop_constraint(
        "spec_sheet_highlight_versions_spec_sheet_id_fkey",
        "spec_sheet_highlight_versions",
        schema="pycrm",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "spec_sheet_highlight_versions_spec_sheet_id_fkey",
        "spec_sheet_highlight_versions",
        "spec_sheets",
        ["spec_sheet_id"],
        ["id"],
        source_schema="pycrm",
        referent_schema="pycrm",
        ondelete="CASCADE",
    )

    # 2. spec_sheet_highlight_regions -> spec_sheet_highlight_versions CASCADE
    op.drop_constraint(
        "spec_sheet_highlight_regions_version_id_fkey",
        "spec_sheet_highlight_regions",
        schema="pycrm",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "spec_sheet_highlight_regions_version_id_fkey",
        "spec_sheet_highlight_regions",
        "spec_sheet_highlight_versions",
        ["version_id"],
        ["id"],
        source_schema="pycrm",
        referent_schema="pycrm",
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # 1. Revert spec_sheet_highlight_versions -> spec_sheets
    op.drop_constraint(
        "spec_sheet_highlight_versions_spec_sheet_id_fkey",
        "spec_sheet_highlight_versions",
        schema="pycrm",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "spec_sheet_highlight_versions_spec_sheet_id_fkey",
        "spec_sheet_highlight_versions",
        "spec_sheets",
        ["spec_sheet_id"],
        ["id"],
        source_schema="pycrm",
        referent_schema="pycrm",
    )

    # 2. Revert spec_sheet_highlight_regions -> spec_sheet_highlight_versions
    op.drop_constraint(
        "spec_sheet_highlight_regions_version_id_fkey",
        "spec_sheet_highlight_regions",
        schema="pycrm",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "spec_sheet_highlight_regions_version_id_fkey",
        "spec_sheet_highlight_regions",
        "spec_sheet_highlight_versions",
        ["version_id"],
        ["id"],
        source_schema="pycrm",
        referent_schema="pycrm",
    )
