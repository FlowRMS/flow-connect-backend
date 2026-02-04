from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "3788145070d2"
down_revision: str | tuple[str, ...] | None = (
    "cascade_del_regions",
    "add_returned_pdf_tables",
    "5630cc7582d0",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
