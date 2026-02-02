from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "5630cc7582d0"
down_revision: str | tuple[str, ...] | None = ("undo_null_sold_to", "a9ce29443448")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
