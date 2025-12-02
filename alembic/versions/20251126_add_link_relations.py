"""add link_relations table

Revision ID: c9gdgp6mze3d
Revises: 032efb9876e4
Create Date: 2025-11-26 21:30:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'c9gdgp6mze3d'
down_revision: str | None = '032efb9876e4'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create link_relations table
    _ = op.create_table(
        'link_relations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_entity_type', sa.SmallInteger(), nullable=False),
        sa.Column('source_entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('target_entity_type', sa.SmallInteger(), nullable=False),
        sa.Column('target_entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='pycrm'
    )

    # Create indexes
    op.create_index(
        'ix_crm_link_relations_source_type_source_id',
        'link_relations',
        ['source_entity_type', 'source_entity_id'],
        schema='pycrm'
    )

    op.create_index(
        'ix_crm_link_relations_target_type_target_id',
        'link_relations',
        ['target_entity_type', 'target_entity_id'],
        schema='pycrm'
    )

    op.create_index(
        'ix_crm_link_relations_source_target',
        'link_relations',
        ['source_entity_type', 'source_entity_id', 'target_entity_type', 'target_entity_id'],
        schema='pycrm'
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_crm_link_relations_source_target', table_name='link_relations', schema='pycrm')
    op.drop_index('ix_crm_link_relations_target_type_target_id', table_name='link_relations', schema='pycrm')
    op.drop_index('ix_crm_link_relations_source_type_source_id', table_name='link_relations', schema='pycrm')

    # Drop table
    op.drop_table('link_relations', schema='pycrm')
