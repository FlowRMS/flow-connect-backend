"""rename_metadata_to_activity_metadata

Revision ID: 22af57481162
Revises: fulfillment_001
Create Date: 2026-01-03 18:46:53.131853

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "22af57481162"
down_revision: str | None = "fulfillment_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "fulfillment_activities",
        "metadata",
        new_column_name="activity_metadata",
        schema="pywarehouse",
    )


def downgrade() -> None:
    op.alter_column(
        "fulfillment_activities",
        "activity_metadata",
        new_column_name="metadata",
        schema="pywarehouse",
    )
