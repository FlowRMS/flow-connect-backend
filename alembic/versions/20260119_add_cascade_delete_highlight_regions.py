"""add_cascade_delete_highlight_regions

Revision ID: cascade_del_regions
Revises: cascade_del_highlights
Create Date: 2026-01-19 18:30:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cascade_del_regions"
down_revision: str | None = "cascade_del_highlights"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # spec_sheet_highlight_regions -> spec_sheet_highlight_versions CASCADE
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
