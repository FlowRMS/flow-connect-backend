from collections.abc import Sequence

revision: str = "d538c52154d8"
down_revision: str | tuple[str, ...] | None = (
    "8a447991abdd",
    "spec_sheet_file_id",
    "add_chat_folders",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
