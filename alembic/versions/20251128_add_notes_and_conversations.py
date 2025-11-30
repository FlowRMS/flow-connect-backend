"""add notes and conversations

Revision ID: a1b2c3d4e5f6
Revises: 51100addf2b2
Create Date: 2025-11-28 10:00:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: str | None = '51100addf2b2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    # Create notes table
    _ = op.create_table(
        'notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('mentions', postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='crm'
    )

    # Create note_conversations table
    _ = op.create_table(
        'note_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('note_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['note_id'], ['crm.notes.id'], name='fk_note_conversations_note_id', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        schema='crm'
    )

    # Create index on note_conversations for efficient lookups
    op.create_index(
        'ix_crm_note_conversations_note_id',
        'note_conversations',
        ['note_id'],
        schema='crm'
    )

def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_crm_note_conversations_note_id', table_name='note_conversations', schema='crm')
    op.drop_table('note_conversations', schema='crm')
    op.drop_table('notes', schema='crm')
