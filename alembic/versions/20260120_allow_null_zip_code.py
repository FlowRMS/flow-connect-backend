"""allow null zip_code in addresses

Revision ID: allow_null_zip_code
Revises: add_commission_statements
Create Date: 2026-01-20

"""

from collections.abc import Sequence

from alembic import op

revision: str = "allow_null_zip_code"
down_revision: str | None = "add_commission_statements"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Allow NULL for zip_code - some addresses may not have zip codes
    op.alter_column(
        "addresses",
        "zip_code",
        nullable=True,
        schema="pycore",
    )


def downgrade() -> None:
    # First update any NULL values to empty string
    op.execute("UPDATE pycore.addresses SET zip_code = '' WHERE zip_code IS NULL")
    # Then make it NOT NULL again
    op.alter_column(
        "addresses",
        "zip_code",
        nullable=False,
        schema="pycore",
    )
