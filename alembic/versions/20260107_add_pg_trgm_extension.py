from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e77b1b398268"
down_revision: str | None = "17288a31ff81"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create pg_trgm extension for similarity() function used in product search
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")


def downgrade() -> None:
    # Note: Dropping the extension could break other functionality that depends on it
    # Only uncomment if you're sure nothing else uses it
    # op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
    pass
