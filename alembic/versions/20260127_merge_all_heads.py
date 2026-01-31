from collections.abc import Sequence

revision: str = "a4dc14d8d606"
down_revision: str | tuple[str, ...] | None = (
    "add_manufacturer_to_items",
    "drop_spec_sheet_folder_path",
    "add_pdf_file_size_to_revisions",
    "add_lead_time_to_items",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
