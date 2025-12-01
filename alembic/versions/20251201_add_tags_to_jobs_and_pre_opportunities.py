"""add_tags_to_jobs_and_pre_opportunities

Revision ID: 0b3a96d1edc3
Revises: a1b2c3d4e5f6
Create Date: 2025-12-01 13:42:38.086928

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0b3a96d1edc3'
down_revision: str | None = 'a1b2c3d4e5f6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add tags column to jobs table
    op.add_column(
        'jobs',
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        schema='crm'
    )

    # Add tags column to pre_opportunities table
    op.add_column(
        'pre_opportunities',
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        schema='crm'
    )


def downgrade() -> None:
    # Remove tags column from pre_opportunities table
    op.drop_column('pre_opportunities', 'tags', schema='crm')

    # Remove tags column from jobs table
    op.drop_column('jobs', 'tags', schema='crm')
