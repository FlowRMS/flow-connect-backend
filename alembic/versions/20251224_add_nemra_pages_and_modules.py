"""add nemra_pages and nemra_modules tables

Revision ID: 16301316601b
Revises: e1dce2e62fd5
Create Date: 2025-12-24 00:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '16301316601b'
down_revision: str | None = 'e1dce2e62fd5'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        'nemra_pages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema='report'
    )
    
    op.create_index('ix_nemra_pages_name', 'nemra_pages', ['name'], schema='report')
    
    _ = op.create_table(
        'nemra_modules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        schema='report'
    )
    
    op.create_index('ix_nemra_modules_name', 'nemra_modules', ['name'], schema='report')
    
    op.execute(sa.text("""
        INSERT INTO report.nemra_pages (name) VALUES
        ('Planning'),
        ('Demand Generation'),
        ('Product Expertise'),
        ('Technology'),
        ('Marketing'),
        ('Notes')
        ON CONFLICT (name) DO NOTHING
    """))
    
    op.execute(sa.text("""
        INSERT INTO report.nemra_modules (name) VALUES
        ('Financial Performance Overview'),
        ('Quarterly Forecast Tracker'),
        ('Goal Alignment Summary'),
        ('Trend Anticipation Dashboard'),
        ('Southeast Opportunity Heatmap'),
        ('Market Share Intelligence'),
        ('Account Planning Matrix'),
        ('Proactive Campaign Execution'),
        ('Drive Conversions'),
        ('Customer Relationship Ownership'),
        ('Speed of Quoting'),
        ('MDF & Co-op Utilization Tracker'),
        ('Field Knowledge'),
        ('Value Delivery'),
        ('Ongoing Self-Training'),
        ('Certification Program Support'),
        ('Strategic Actions'),
        ('Strategic Asks'),
        ('FlowFree Integrations'),
        ('Flow Realtime Collaboration Suite'),
        ('Data Pipes'),
        ('Shared Product Catalogs'),
        ('Data-Driven Opportunities'),
        ('AI Tools - Flow'),
        ('AI Tools - Flow Connect'),
        ('Emerging Tools & Roadmaps'),
        ('Digital Presence'),
        ('Resource Utilization')
        ON CONFLICT (name) DO NOTHING
    """))


def downgrade() -> None:
    op.drop_index('ix_nemra_modules_name', table_name='nemra_modules', schema='report')
    op.drop_table('nemra_modules', schema='report')
    
    op.drop_index('ix_nemra_pages_name', table_name='nemra_pages', schema='report')
    op.drop_table('nemra_pages', schema='report')

