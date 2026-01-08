
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'd5e6f7182031'
down_revision: Union[str, None] = 'c4d5e6f71920'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def add_column_if_missing(table: str, column_name: str, column: sa.Column, schema: str, existing: set[str]) -> None:
    if column_name not in existing:
        op.add_column(table, column, schema=schema)


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names(schema='pycommission'))
    
    # ===== ORDER BALANCES TABLE =====
    if 'order_balances' not in existing_tables:
        op.create_table('order_balances',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('quantity', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('subtotal', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('total', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('discount', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('discount_rate', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission_rate', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission_discount', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission_discount_rate', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('shipping_balance', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('cancelled_balance', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('freight_charge_balance', sa.Numeric(18, 6), nullable=False, server_default='0'),
            schema='pycommission'
        )
    else:
        existing = {col['name'] for col in inspector.get_columns('order_balances', schema='pycommission')}
        for col_name, col_def in [
            ('quantity', sa.Column('quantity', sa.Numeric(18, 6), nullable=True)),
            ('subtotal', sa.Column('subtotal', sa.Numeric(18, 6), nullable=True)),
            ('total', sa.Column('total', sa.Numeric(18, 6), nullable=True)),
            ('commission', sa.Column('commission', sa.Numeric(18, 6), nullable=True)),
            ('discount', sa.Column('discount', sa.Numeric(18, 6), nullable=True)),
            ('discount_rate', sa.Column('discount_rate', sa.Numeric(18, 6), nullable=True)),
            ('commission_rate', sa.Column('commission_rate', sa.Numeric(18, 6), nullable=True)),
            ('commission_discount', sa.Column('commission_discount', sa.Numeric(18, 6), nullable=True)),
            ('commission_discount_rate', sa.Column('commission_discount_rate', sa.Numeric(18, 6), nullable=True)),
            ('shipping_balance', sa.Column('shipping_balance', sa.Numeric(18, 6), nullable=True)),
            ('cancelled_balance', sa.Column('cancelled_balance', sa.Numeric(18, 6), nullable=True)),
            ('freight_charge_balance', sa.Column('freight_charge_balance', sa.Numeric(18, 6), nullable=True)),
        ]:
            add_column_if_missing('order_balances', col_name, col_def, 'pycommission', existing)

    # ===== ORDERS TABLE =====
    if 'orders' not in existing_tables:
        op.create_table('orders',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('order_number', sa.String(255), nullable=False),
            sa.Column('entity_date', sa.Date, nullable=False),
            sa.Column('due_date', sa.Date, nullable=False),
            sa.Column('factory_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('sold_to_customer_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('bill_to_customer_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('quote_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('balance_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('published', sa.Boolean, nullable=False, server_default='true'),
            sa.Column('creation_type', sa.Integer, nullable=False, server_default='1'),
            sa.Column('status', sa.Integer, nullable=False, server_default='1'),
            sa.Column('order_type', sa.Integer, nullable=False, server_default='1'),
            sa.Column('header_status', sa.Integer, nullable=False, server_default='1'),
            sa.Column('shipping_terms', sa.String(255), nullable=True),
            sa.Column('freight_terms', sa.String(255), nullable=True),
            sa.Column('mark_number', sa.String(255), nullable=True),
            sa.Column('fact_so_number', sa.String(255), nullable=True),
            sa.Column('ship_date', sa.Date, nullable=True),
            sa.Column('projected_ship_date', sa.Date, nullable=True),
            sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['factory_id'], ['pycore.factories.id']),
            sa.ForeignKeyConstraint(['sold_to_customer_id'], ['pycore.customers.id']),
            sa.ForeignKeyConstraint(['bill_to_customer_id'], ['pycore.customers.id']),
            sa.ForeignKeyConstraint(['balance_id'], ['pycommission.order_balances.id']),
            sa.ForeignKeyConstraint(['created_by_id'], ['public.users.id']),
            schema='pycommission'
        )
    else:
        existing = {col['name'] for col in inspector.get_columns('orders', schema='pycommission')}
        for col_name, col_def in [
            ('job_id', sa.Column('job_id', postgresql.UUID(as_uuid=True), nullable=True)),
            ('bill_to_customer_id', sa.Column('bill_to_customer_id', postgresql.UUID(as_uuid=True), nullable=True)),
            ('balance_id', sa.Column('balance_id', postgresql.UUID(as_uuid=True), nullable=True)),
            ('created_by_id', sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True)),
            ('created_at', sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=True)),
            ('published', sa.Column('published', sa.Boolean, nullable=True)),
            ('creation_type', sa.Column('creation_type', sa.Integer, nullable=True)),
            ('order_type', sa.Column('order_type', sa.Integer, nullable=True)),
            ('header_status', sa.Column('header_status', sa.Integer, nullable=True)),
            ('shipping_terms', sa.Column('shipping_terms', sa.String(255), nullable=True)),
            ('freight_terms', sa.Column('freight_terms', sa.String(255), nullable=True)),
            ('mark_number', sa.Column('mark_number', sa.String(255), nullable=True)),
            ('fact_so_number', sa.Column('fact_so_number', sa.String(255), nullable=True)),
            ('ship_date', sa.Column('ship_date', sa.Date, nullable=True)),
            ('projected_ship_date', sa.Column('projected_ship_date', sa.Date, nullable=True)),
            ('quote_id', sa.Column('quote_id', postgresql.UUID(as_uuid=True), nullable=True)),
        ]:
            add_column_if_missing('orders', col_name, col_def, 'pycommission', existing)

    # ===== ORDER DETAILS TABLE =====
    if 'order_details' not in existing_tables:
        op.create_table('order_details',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('item_number', sa.Integer, nullable=False),
            sa.Column('quantity', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('unit_price', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('subtotal', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('total', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('total_line_commission', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission_rate', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission_discount_rate', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission_discount', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('discount_rate', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('discount', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('division_factor', sa.Numeric(18, 6), nullable=True),
            sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('product_name_adhoc', sa.String(255), nullable=True),
            sa.Column('product_description_adhoc', sa.Text, nullable=True),
            sa.Column('uom_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('end_user_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('lead_time', sa.String(255), nullable=True),
            sa.Column('note', sa.String(2000), nullable=True),
            sa.Column('freight_charge', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('status', sa.Integer, nullable=False, server_default='1'),
            sa.Column('shipping_balance', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('cancelled_balance', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.ForeignKeyConstraint(['order_id'], ['pycommission.orders.id']),
            sa.ForeignKeyConstraint(['product_id'], ['pycore.products.id']),
            sa.ForeignKeyConstraint(['uom_id'], ['pycore.product_uoms.id']),
            sa.ForeignKeyConstraint(['end_user_id'], ['pycore.customers.id']),
            schema='pycommission'
        )
        op.create_index('ix_pycommission_order_details_order_id', 'order_details', ['order_id'], schema='pycommission')

    # ===== INVOICE BALANCES TABLE =====
    if 'invoice_balances' not in existing_tables:
        op.create_table('invoice_balances',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('quantity', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('subtotal', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('total', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('discount', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('discount_rate', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission_rate', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission_discount', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission_discount_rate', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('paid_balance', sa.Numeric(18, 6), nullable=False, server_default='0'),
            schema='pycommission'
        )

    # ===== INVOICES TABLE =====
    if 'invoices' not in existing_tables:
        op.create_table('invoices',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('invoice_number', sa.String(255), nullable=False),
            sa.Column('entity_date', sa.Date, nullable=False),
            sa.Column('factory_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('due_date', sa.Date, nullable=True),
            sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('balance_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('published', sa.Boolean, nullable=False, server_default='true'),
            sa.Column('locked', sa.Boolean, nullable=False, server_default='false'),
            sa.Column('creation_type', sa.Integer, nullable=False, server_default='1'),
            sa.Column('status', sa.Integer, nullable=False, server_default='1'),
            sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['factory_id'], ['pycore.factories.id']),
            sa.ForeignKeyConstraint(['order_id'], ['pycommission.orders.id']),
            sa.ForeignKeyConstraint(['balance_id'], ['pycommission.invoice_balances.id']),
            sa.ForeignKeyConstraint(['created_by_id'], ['public.users.id']),
            schema='pycommission'
        )
    else:
        existing = {col['name'] for col in inspector.get_columns('invoices', schema='pycommission')}
        for col_name, col_def in [
            ('balance_id', sa.Column('balance_id', postgresql.UUID(as_uuid=True), nullable=True)),
            ('created_by_id', sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True)),
            ('created_at', sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=True)),
        ]:
            add_column_if_missing('invoices', col_name, col_def, 'pycommission', existing)

    # ===== INVOICE DETAILS TABLE =====
    if 'invoice_details' not in existing_tables:
        op.create_table('invoice_details',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('invoice_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('order_detail_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('item_number', sa.Integer, nullable=False),
            sa.Column('quantity', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('unit_price', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('subtotal', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('total', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('total_line_commission', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission_rate', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission_discount_rate', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('commission_discount', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('discount_rate', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('discount', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.Column('division_factor', sa.Numeric(18, 6), nullable=True),
            sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('product_name_adhoc', sa.String(255), nullable=True),
            sa.Column('product_description_adhoc', sa.Text, nullable=True),
            sa.Column('uom_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('end_user_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('lead_time', sa.String(255), nullable=True),
            sa.Column('note', sa.String(2000), nullable=True),
            sa.Column('status', sa.Integer, nullable=False, server_default='1'),
            sa.Column('invoiced_balance', sa.Numeric(18, 6), nullable=False, server_default='0'),
            sa.ForeignKeyConstraint(['invoice_id'], ['pycommission.invoices.id']),
            sa.ForeignKeyConstraint(['order_detail_id'], ['pycommission.order_details.id']),
            sa.ForeignKeyConstraint(['product_id'], ['pycore.products.id']),
            sa.ForeignKeyConstraint(['uom_id'], ['pycore.product_uoms.id']),
            sa.ForeignKeyConstraint(['end_user_id'], ['pycore.customers.id']),
            schema='pycommission'
        )
        op.create_index('ix_pycommission_invoice_details_invoice_id', 'invoice_details', ['invoice_id'], schema='pycommission')
        op.create_index('ix_pycommission_invoice_details_order_detail_id', 'invoice_details', ['order_detail_id'], schema='pycommission')

    # ===== SPLIT RATE TABLES =====
    if 'order_split_rates' not in existing_tables:
        op.create_table('order_split_rates',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('order_detail_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('split_rate', sa.Numeric(5, 4), nullable=False),
            sa.Column('position', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['order_detail_id'], ['pycommission.order_details.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['public.users.id']),
            schema='pycommission'
        )
        op.create_index('ix_pycommission_order_split_rates_order_detail_id', 'order_split_rates', ['order_detail_id'], schema='pycommission')

    if 'order_inside_reps' not in existing_tables:
        op.create_table('order_inside_reps',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('order_detail_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('split_rate', sa.Numeric(5, 4), nullable=False),
            sa.Column('position', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['order_detail_id'], ['pycommission.order_details.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['public.users.id']),
            schema='pycommission'
        )
        op.create_index('ix_pycommission_order_inside_reps_order_detail_id', 'order_inside_reps', ['order_detail_id'], schema='pycommission')

    if 'invoice_split_rates' not in existing_tables:
        op.create_table('invoice_split_rates',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('invoice_detail_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('split_rate', sa.Numeric(5, 4), nullable=False),
            sa.Column('position', sa.Integer, nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=False), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['invoice_detail_id'], ['pycommission.invoice_details.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['public.users.id']),
            schema='pycommission'
        )
        op.create_index('ix_pycommission_invoice_split_rates_invoice_detail_id', 'invoice_split_rates', ['invoice_detail_id'], schema='pycommission')


def downgrade() -> None:
    # Drop in reverse order
    op.drop_table('invoice_split_rates', schema='pycommission', if_exists=True)
    op.drop_table('order_inside_reps', schema='pycommission', if_exists=True)
    op.drop_table('order_split_rates', schema='pycommission', if_exists=True)
    op.drop_table('invoice_details', schema='pycommission', if_exists=True)
    op.drop_table('invoices', schema='pycommission', if_exists=True)
    op.drop_table('invoice_balances', schema='pycommission', if_exists=True)
    op.drop_table('order_details', schema='pycommission', if_exists=True)
    op.drop_table('orders', schema='pycommission', if_exists=True)
    op.drop_table('order_balances', schema='pycommission', if_exists=True)
