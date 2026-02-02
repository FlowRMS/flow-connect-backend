from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "262a851d61ee"
down_revision: str | None = "b2c3d4e5f607"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
