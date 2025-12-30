"""adding job to quotes and orders

Revision ID: cd1f6cbd8751
Revises: 7a8b9c0d1e2f
Create Date: 2025-12-27 15:02:46.305301

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "cd1f6cbd8751"
down_revision: str | None = "7a8b9c0d1e2f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add job_id column to quotes table
    op.add_column(
        "quotes",
        sa.Column(
            "job_id",
            sa.UUID(),
            sa.ForeignKey("pycrm.jobs.id"),
            nullable=True,
            default=None,
        ),
        schema="pycrm",
    )

    # Add job_id column to orders table
    op.add_column(
        "orders",
        sa.Column(
            "job_id",
            sa.UUID(),
            sa.ForeignKey("pycrm.jobs.id"),
            nullable=True,
            default=None,
        ),
        schema="pycommission",
    )


def downgrade() -> None:
    pass
