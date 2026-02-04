from collections.abc import Sequence

revision: str = "a4dc14d8d606"
down_revision: str | tuple[str, ...] | None = "drop_spec_sheet_folder_path"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
