from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "896105b07ca6"
down_revision: str | None = "e77b1b398268"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Change quantity column from INTEGER to NUMERIC(18,6).

    Allows fractional quantities (e.g., 2.5 kg, 0.75 units).
    Existing integer values are preserved (e.g., 5 -> 5.000000).
    """
    op.execute(
        """
        ALTER TABLE pywarehouse.location_product_assignments
        ALTER COLUMN quantity TYPE NUMERIC(18,6)
        USING quantity::NUMERIC(18,6)
        """
    )


def downgrade() -> None:
    """Revert quantity column from NUMERIC(18,6) back to INTEGER.

    WARNING: Decimal values will be truncated (e.g., 5.75 -> 5).
    """
    op.execute(
        """
        ALTER TABLE pywarehouse.location_product_assignments
        ALTER COLUMN quantity TYPE INTEGER
        USING quantity::INTEGER
        """
    )
