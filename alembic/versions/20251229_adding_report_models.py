"""adding report models

Revision ID: 983952e7b210
Revises: 9d87acc00979
Create Date: 2025-12-29 07:44:25.009824

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "983952e7b210"
down_revision: str | None = "9d87acc00979"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "report_templates",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("report_template_name", sa.String(), nullable=False),
        sa.Column("report_type", sa.SmallInteger(), nullable=False),
        sa.Column("report_config", JSONB(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema="report",
    )


def downgrade() -> None:
    op.drop_table("report_templates", schema="report")
