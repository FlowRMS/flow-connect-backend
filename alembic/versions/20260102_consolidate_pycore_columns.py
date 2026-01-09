from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c4d5e6f71920'
down_revision: str | None = 'b2c3d4e5f607'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Products table enhancements
    op.add_column('products', sa.Column('factory_id', postgresql.UUID(as_uuid=True), nullable=True), schema='pycore')
    op.add_column('products', sa.Column('product_category_id', postgresql.UUID(as_uuid=True), nullable=True), schema='pycore')
    op.add_column('products', sa.Column('abc_class', sa.String(length=1), nullable=True), schema='pycore')
    op.add_column('products', sa.Column('lead_time_days', sa.Integer(), nullable=True), schema='pycore')
    op.add_column('products', sa.Column('reorder_point', sa.Numeric(precision=15, scale=4), nullable=True), schema='pycore')
    op.add_column('products', sa.Column('order_quantity', sa.Numeric(precision=15, scale=4), nullable=True), schema='pycore')
    op.add_column('products', sa.Column('safety_stock', sa.Numeric(precision=15, scale=4), nullable=True), schema='pycore')
    op.add_column('products', sa.Column('max_stock', sa.Numeric(precision=15, scale=4), nullable=True), schema='pycore')
    op.add_column('products', sa.Column('created_at', sa.DateTime(timezone=False), nullable=True), schema='pycore')
    op.add_column('products', sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True), schema='pycore')
    op.add_column('products', sa.Column('updated_at', sa.DateTime(timezone=False), nullable=True), schema='pycore')
    op.add_column('products', sa.Column('updated_by_id', postgresql.UUID(as_uuid=True), nullable=True), schema='pycore')
    
    op.create_foreign_key('fk_products_factory_id', 'products', 'factories', ['factory_id'], ['id'], source_schema='pycore', referent_schema='pycore')
    op.create_foreign_key('fk_products_product_category_id', 'products', 'product_categories', ['product_category_id'], ['id'], source_schema='pycore', referent_schema='pycore')
    op.create_foreign_key('fk_products_created_by_id', 'products', 'users', ['created_by_id'], ['id'], source_schema='pycore', referent_schema='public')
    op.create_foreign_key('fk_products_updated_by_id', 'products', 'users', ['updated_by_id'], ['id'], source_schema='pycore', referent_schema='public')
    
    # Product categories enhancements
    op.add_column('product_categories', sa.Column('parent_category_id', postgresql.UUID(as_uuid=True), nullable=True), schema='pycore')
    op.add_column('product_categories', sa.Column('sort_order', sa.Integer(), nullable=True), schema='pycore')
    op.create_foreign_key('fk_product_categories_parent_id', 'product_categories', 'product_categories', ['parent_category_id'], ['id'], source_schema='pycore', referent_schema='pycore')
    
    # Product UOMs enhancements
    op.add_column('product_uoms', sa.Column('conversion_factor', sa.Numeric(precision=15, scale=6), nullable=True), schema='pycore')
    op.add_column('product_uoms', sa.Column('is_base_uom', sa.Boolean(), nullable=True), schema='pycore')
    op.add_column('product_uoms', sa.Column('barcode', sa.String(length=100), nullable=True), schema='pycore')
    
    # Customers enhancements
    op.add_column('customers', sa.Column('external_id', sa.String(length=100), nullable=True), schema='pycore')
    op.add_column('customers', sa.Column('customer_type', sa.String(length=50), nullable=True), schema='pycore')
    op.add_column('customers', sa.Column('payment_terms', sa.String(length=100), nullable=True), schema='pycore')
    op.add_column('customers', sa.Column('credit_limit', sa.Numeric(precision=15, scale=2), nullable=True), schema='pycore')
    op.add_column('customers', sa.Column('tax_exempt', sa.Boolean(), nullable=False, server_default='false'), schema='pycore')
    op.add_column('customers', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'), schema='pycore')


def downgrade() -> None:
    # Customers
    op.drop_column('customers', 'is_active', schema='pycore')
    op.drop_column('customers', 'tax_exempt', schema='pycore')
    op.drop_column('customers', 'credit_limit', schema='pycore')
    op.drop_column('customers', 'payment_terms', schema='pycore')
    op.drop_column('customers', 'customer_type', schema='pycore')
    op.drop_column('customers', 'external_id', schema='pycore')
    
    # Product UOMs
    op.drop_column('product_uoms', 'barcode', schema='pycore')
    op.drop_column('product_uoms', 'is_base_uom', schema='pycore')
    op.drop_column('product_uoms', 'conversion_factor', schema='pycore')
    
    # Product categories
    op.drop_constraint('fk_product_categories_parent_id', 'product_categories', schema='pycore', type_='foreignkey')
    op.drop_column('product_categories', 'sort_order', schema='pycore')
    op.drop_column('product_categories', 'parent_category_id', schema='pycore')
    
    # Products
    op.drop_constraint('fk_products_updated_by_id', 'products', schema='pycore', type_='foreignkey')
    op.drop_constraint('fk_products_created_by_id', 'products', schema='pycore', type_='foreignkey')
    op.drop_constraint('fk_products_product_category_id', 'products', schema='pycore', type_='foreignkey')
    op.drop_constraint('fk_products_factory_id', 'products', schema='pycore', type_='foreignkey')
    op.drop_column('products', 'updated_by_id', schema='pycore')
    op.drop_column('products', 'updated_at', schema='pycore')
    op.drop_column('products', 'created_by_id', schema='pycore')
    op.drop_column('products', 'created_at', schema='pycore')
    op.drop_column('products', 'max_stock', schema='pycore')
    op.drop_column('products', 'safety_stock', schema='pycore')
    op.drop_column('products', 'order_quantity', schema='pycore')
    op.drop_column('products', 'reorder_point', schema='pycore')
    op.drop_column('products', 'lead_time_days', schema='pycore')
    op.drop_column('products', 'abc_class', schema='pycore')
    op.drop_column('products', 'product_category_id', schema='pycore')
    op.drop_column('products', 'factory_id', schema='pycore')
