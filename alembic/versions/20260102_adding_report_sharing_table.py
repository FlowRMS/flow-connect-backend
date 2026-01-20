"""adding_report_sharing_table

Revision ID: add_report_sharing_table
Revises: insert_default_uoms_001
Create Date: 2026-01-02 16:59:25.626923

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_report_sharing_table'
down_revision: str | None = 'add_chat_folders'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    _ = op.create_table(
        'shared_templates',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('report_template_id', sa.UUID(), nullable=False),
        sa.Column('shared_with_user_id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        schema='report'
    )
    # indexes for report_template_id and shared_with_user_id
    _ = op.create_index('idx_shared_templates_report_template_id', 'shared_templates', ['report_template_id'], schema='report')
    _ = op.create_index('idx_shared_templates_shared_with_user_id', 'shared_templates', ['shared_with_user_id'], schema='report')
    # foreign key for report_template_id - fix: the table name must be without schema prefix
    _ = op.create_foreign_key(
        'fk_shared_templates_report_template_id',
        source_table='shared_templates',
        referent_table='report_templates',
        local_cols=['report_template_id'],
        remote_cols=['id'],
        source_schema='report',
        referent_schema='report',
        ondelete='CASCADE'
    )

    _ = op.add_column('report_templates', sa.Column('organization_shared', sa.Boolean(), nullable=True, server_default=sa.false()), schema='report')

    _ = op.execute("UPDATE report.report_templates SET organization_shared = FALSE")
    _ = op.alter_column('report_templates', 'organization_shared', nullable=False, schema='report')

    # constraint unique on report_template_id and shared_with_user_id combination
    _ = op.create_unique_constraint('uq_shared_templates_report_template_id_shared_with_user_id', 'shared_templates', ['report_template_id', 'shared_with_user_id'], schema='report')

    # add report template created at server default now
    _ = op.alter_column('report_templates', 'created_at', server_default=sa.text('now()'), schema='report')

def downgrade() -> None:
    _ = op.drop_column('report_templates', 'organization_shared', schema='report')
    _ = op.drop_table('shared_templates', schema='report')
    _ = op.alter_column('report_templates', 'created_at', server_default=None, schema='report')