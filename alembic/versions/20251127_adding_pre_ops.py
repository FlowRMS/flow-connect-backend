"""adding pre ops

Revision ID: 51100addf2b2
Revises: c9gdgp6mze3d
Create Date: 2025-11-27 15:54:57.713581

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
# revision identifiers, used by Alembic.
revision: str = '51100addf2b2'
down_revision: str | None = 'c9gdgp6mze3d'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    # Create pre_opportunity_balances table (created first as it's referenced by pre_opportunities)
    _ = op.create_table(
        'pre_opportunity_balances',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subtotal', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('total', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('discount', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('discount_rate', sa.Numeric(precision=5, scale=2), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='crm'
    )

    # Create pre_opportunities table
    _ = op.create_table(
        'pre_opportunities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.SmallInteger(), nullable=False),
        sa.Column('entity_number', sa.String(length=255), nullable=False, unique=True),
        sa.Column('entity_date', sa.Date(), nullable=False),
        sa.Column('exp_date', sa.Date(), nullable=True),
        sa.Column('revise_date', sa.Date(), nullable=True),
        sa.Column('accept_date', sa.Date(), nullable=True),
        sa.Column('sold_to_customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sold_to_customer_address_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('bill_to_customer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('bill_to_customer_address_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('balance_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_terms', sa.String(length=255), nullable=True),
        sa.Column('customer_ref', sa.String(length=255), nullable=True),
        sa.Column('freight_terms', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['sold_to_customer_id'], ['core.customers.id'], name='fk_pre_opportunities_sold_to_customer'),
        sa.ForeignKeyConstraint(['bill_to_customer_id'], ['core.customers.id'], name='fk_pre_opportunities_bill_to_customer'),
        sa.ForeignKeyConstraint(['job_id'], ['crm.jobs.id'], name='fk_pre_opportunities_job'),
        sa.ForeignKeyConstraint(['balance_id'], ['crm.pre_opportunity_balances.id'], name='fk_pre_opportunities_balance'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('balance_id', name='uq_pre_opportunities_balance_id'),
        schema='crm'
    )

    # Create pre_opportunity_details table
    _ = op.create_table(
        'pre_opportunity_details',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('pre_opportunity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('item_number', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('subtotal', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('discount_rate', sa.Numeric(precision=5, scale=2), server_default='0', nullable=False),
        sa.Column('discount', sa.Numeric(precision=10, scale=2), server_default='0', nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_cpn_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('end_user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('lead_time', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['pre_opportunity_id'], ['crm.pre_opportunities.id'], name='fk_pre_opportunity_details_pre_opportunity'),
        sa.ForeignKeyConstraint(['product_id'], ['core.products.id'], name='fk_pre_opportunity_details_product'),
        sa.ForeignKeyConstraint(['factory_id'], ['core.factories.id'], name='fk_pre_opportunity_details_factory'),
        sa.ForeignKeyConstraint(['end_user_id'], ['core.customers.id'], name='fk_pre_opportunity_details_end_user'),
        sa.PrimaryKeyConstraint('id'),
        schema='crm'
    )

    # Create index on pre_opportunity_details for efficient lookups
    op.create_index(
        'ix_crm_pre_opportunity_details_pre_opportunity_id',
        'pre_opportunity_details',
        ['pre_opportunity_id'],
        schema='crm'
    )

def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_crm_pre_opportunity_details_pre_opportunity_id', table_name='pre_opportunity_details', schema='crm')
    op.drop_table('pre_opportunity_details', schema='crm')
    op.drop_table('pre_opportunities', schema='crm')
    op.drop_table('pre_opportunity_balances', schema='crm')
