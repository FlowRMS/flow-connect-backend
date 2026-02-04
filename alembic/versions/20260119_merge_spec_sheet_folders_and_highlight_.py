from collections.abc import Sequence

revision: str = "96d32cf858d0"
down_revision: str | tuple[str, ...] | None = (
    "highlight_tags_001",
    "create_spec_sheet_folders",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
