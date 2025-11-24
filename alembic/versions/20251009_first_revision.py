"""first revision

Revision ID: 6f462a3f0a59
Revises: 
Create Date: 2025-10-09 16:43:51.169236

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = '6f462a3f0a59'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    _ = op.create_table(
        'report_templates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('report_template_name', sa.String(), nullable=False),
        sa.Column('report_type', sa.SmallInteger(), nullable=False),
        sa.Column('report_config', JSONB(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='report'
    )

def downgrade() -> None:
    op.drop_table('report_templates', schema='report')