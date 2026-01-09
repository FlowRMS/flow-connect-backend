"""add nemra_page_modules junction table and relationships

Revision ID: dce57ae2783a
Revises: 16301316601b
Create Date: 2025-12-25 00:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'dce57ae2783a'
down_revision: str | None = '16301316601b'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        'nemra_page_modules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('page_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('module_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['page_id'], ['report.nemra_pages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['report.nemra_modules.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('page_id', 'module_id', name='uq_nemra_page_modules_page_module'),
        schema='report'
    )
    
    op.create_index('ix_nemra_page_modules_page_id', 'nemra_page_modules', ['page_id'], schema='report')
    op.create_index('ix_nemra_page_modules_module_id', 'nemra_page_modules', ['module_id'], schema='report')
    
    op.execute(sa.text("""
        INSERT INTO report.nemra_page_modules (page_id, module_id)
        SELECT p.id, m.id
        FROM report.nemra_pages p
        CROSS JOIN report.nemra_modules m
        WHERE (p.name = 'Planning' AND m.name IN (
            'Financial Performance Overview',
            'Quarterly Forecast Tracker',
            'Goal Alignment Summary',
            'Trend Anticipation Dashboard',
            'Southeast Opportunity Heatmap',
            'Market Share Intelligence',
            'Account Planning Matrix'
        ))
        OR (p.name = 'Demand Generation' AND m.name IN (
            'Proactive Campaign Execution',
            'Drive Conversions',
            'Customer Relationship Ownership',
            'Speed of Quoting',
            'MDF & Co-op Utilization Tracker'
        ))
        OR (p.name = 'Product Expertise' AND m.name IN (
            'Field Knowledge',
            'Value Delivery',
            'Ongoing Self-Training',
            'Certification Program Support',
            'Strategic Actions',
            'Strategic Asks'
        ))
        OR (p.name = 'Technology' AND m.name IN (
            'FlowFree Integrations',
            'Flow Realtime Collaboration Suite',
            'Data Pipes',
            'Shared Product Catalogs',
            'Data-Driven Opportunities',
            'AI Tools - Flow',
            'AI Tools - Flow Connect',
            'Emerging Tools & Roadmaps',
            'Strategic Actions',
            'Strategic Asks'
        ))
        OR (p.name = 'Marketing' AND m.name IN (
            'Digital Presence',
            'Resource Utilization',
            'Strategic Actions',
            'Strategic Asks'
        ))
        ON CONFLICT (page_id, module_id) DO NOTHING
    """))


def downgrade() -> None:
    op.drop_index('ix_nemra_page_modules_module_id', table_name='nemra_page_modules', schema='report')
    op.drop_index('ix_nemra_page_modules_page_id', table_name='nemra_page_modules', schema='report')
    op.drop_table('nemra_page_modules', schema='report')

