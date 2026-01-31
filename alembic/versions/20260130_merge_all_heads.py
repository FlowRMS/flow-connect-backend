from collections.abc import Sequence

revision: str = "2482591dc2ad"
down_revision: str | tuple[str, ...] | None = ("a4dc14d8d606", "14c956003e6b")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
