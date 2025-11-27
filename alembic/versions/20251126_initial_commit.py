"""initial commit

Revision ID: 032efb9876e4
Revises:
Create Date: 2025-11-26 20:04:40.142940

"""
import uuid
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '032efb9876e4'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create schema
    op.execute('CREATE SCHEMA IF NOT EXISTS crm')

    # Create companies table
    _ = op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('company_source_type', sa.SmallInteger(), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('parent_company_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='crm'
    )
    
    # add unique constraint on company name and company_source_type
    op.create_unique_constraint(
        'uq_companies_name_source_type',
        'companies',
        ['name', 'company_source_type'],
        schema='crm'
    )

    # Create contacts table
    _ = op.create_table(
        'contacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('role', sa.String(length=100), nullable=True),
        sa.Column('territory', sa.String(length=100), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['crm.companies.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='crm'
    )

    # Create addresses table
    _ = op.create_table(
        'addresses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('address_type', sa.SmallInteger(), nullable=False),
        sa.Column('address_line_1', sa.String(length=255), nullable=True),
        sa.Column('address_line_2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('zip_code', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['crm.companies.id']),
        sa.PrimaryKeyConstraint('id'),
        schema='crm'
    )

    # Create job_statuses table
    _ = op.create_table(
        'job_statuses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        schema='crm'
    )
    
    statuses = [
        "BID",
        "BUY",
        "COMPLETE",
    ]
    for status in statuses:
        op.execute(
            sa.text(
                "INSERT INTO crm.job_statuses (id, name) VALUES (:id, :name)"
            ).bindparams(id=uuid.uuid4(), name=status
            ),
        )

    # Create jobs table
    _ = op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_name', sa.String(length=255), nullable=False),
        sa.Column('status_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('job_type', sa.Text(), nullable=True),
        sa.Column('structural_details', sa.Text(), nullable=True),
        sa.Column('structural_information', sa.Text(), nullable=True),
        sa.Column('additional_information', sa.Text(), nullable=True),
        sa.Column('requester_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('job_owner_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['status_id'], ['crm.job_statuses.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_name'),
        schema='crm'
    )

    # Create tasks table
    _ = op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('status', sa.SmallInteger(), nullable=False),
        sa.Column('priority', sa.SmallInteger(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('assigned_to_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='crm'
    )

    # Create task_relations table
    _ = op.create_table(
        'task_relations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('related_type', sa.SmallInteger(), nullable=False),
        sa.Column('related_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['crm.tasks.id'], name='fk_task_relations_task_id'),
        sa.PrimaryKeyConstraint('id'),
        schema='crm'
    )

    # Create index on task_relations
    op.create_index(
        'ix_crm_task_relations_task_id_related_type_related_id',
        'task_relations',
        ['task_id', 'related_type', 'related_id'],
        schema='crm'
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_crm_task_relations_task_id_related_type_related_id', table_name='task_relations', schema='crm')
    op.drop_table('task_relations', schema='crm')
    op.drop_table('tasks', schema='crm')
    op.drop_table('jobs', schema='crm')
    op.drop_table('job_statuses', schema='crm')
    op.drop_table('addresses', schema='crm')
    op.drop_table('contacts', schema='crm')
    op.drop_table('companies', schema='crm')

    # Drop schema
    op.execute('DROP SCHEMA IF EXISTS crm CASCADE')
