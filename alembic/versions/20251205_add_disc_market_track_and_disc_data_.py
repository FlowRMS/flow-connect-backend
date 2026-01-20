"""add disc_market_track and disc_data_search tables

Revision ID: e1dce2e62fd5
Revises: add_chat_folders
Create Date: 2025-12-05 02:39:08.118907

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e1dce2e62fd5'
down_revision: str | None = 'add_chat_folders'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create disc schema
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS disc"))
    
    # Create disc_market_track table
    _ = op.create_table(
        'disc_market_track',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('section', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('fips_code', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        schema='disc'
    )
    
    # Create indexes for disc_market_track
    op.create_index('ix_disc_market_track_section', 'disc_market_track', ['section'], schema='disc')
    op.create_index('ix_disc_market_track_location', 'disc_market_track', ['location'], schema='disc')
    op.create_index('ix_disc_market_track_fips_code', 'disc_market_track', ['fips_code'], schema='disc')
    op.create_index('ix_disc_market_track_category', 'disc_market_track', ['category'], schema='disc')
    op.create_index('ix_disc_market_track_year', 'disc_market_track', ['year'], schema='disc')
    op.create_index('idx_disc_market_track_year_category', 'disc_market_track', ['year', 'category'], schema='disc')
    op.create_index('idx_disc_market_track_location_year', 'disc_market_track', ['location', 'year'], schema='disc')
    
    # Create disc_data_search table
    _ = op.create_table(
        'disc_data_search',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('state', sa.String(), nullable=False),
        sa.Column('county', sa.String(), nullable=False),
        sa.Column('fips_code', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        schema='disc'
    )
    
    # Create indexes for disc_data_search
    op.create_index('ix_disc_data_search_state', 'disc_data_search', ['state'], schema='disc')
    op.create_index('ix_disc_data_search_county', 'disc_data_search', ['county'], schema='disc')
    op.create_index('ix_disc_data_search_fips_code', 'disc_data_search', ['fips_code'], schema='disc')
    op.create_index('ix_disc_data_search_category', 'disc_data_search', ['category'], schema='disc')
    op.create_index('ix_disc_data_search_year', 'disc_data_search', ['year'], schema='disc')
    op.create_index('idx_disc_data_search_state_year', 'disc_data_search', ['state', 'year'], schema='disc')
    op.create_index('idx_disc_data_search_year_category', 'disc_data_search', ['year', 'category'], schema='disc')
    op.create_index('idx_disc_data_search_fips_year', 'disc_data_search', ['fips_code', 'year'], schema='disc')


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_disc_data_search_fips_year', table_name='disc_data_search', schema='disc')
    op.drop_index('idx_disc_data_search_year_category', table_name='disc_data_search', schema='disc')
    op.drop_index('idx_disc_data_search_state_year', table_name='disc_data_search', schema='disc')
    op.drop_index('ix_disc_data_search_year', table_name='disc_data_search', schema='disc')
    op.drop_index('ix_disc_data_search_category', table_name='disc_data_search', schema='disc')
    op.drop_index('ix_disc_data_search_fips_code', table_name='disc_data_search', schema='disc')
    op.drop_index('ix_disc_data_search_county', table_name='disc_data_search', schema='disc')
    op.drop_index('ix_disc_data_search_state', table_name='disc_data_search', schema='disc')
    
    op.drop_index('idx_disc_market_track_location_year', table_name='disc_market_track', schema='disc')
    op.drop_index('idx_disc_market_track_year_category', table_name='disc_market_track', schema='disc')
    op.drop_index('ix_disc_market_track_year', table_name='disc_market_track', schema='disc')
    op.drop_index('ix_disc_market_track_category', table_name='disc_market_track', schema='disc')
    op.drop_index('ix_disc_market_track_fips_code', table_name='disc_market_track', schema='disc')
    op.drop_index('ix_disc_market_track_location', table_name='disc_market_track', schema='disc')
    op.drop_index('ix_disc_market_track_section', table_name='disc_market_track', schema='disc')
    
    # Drop tables
    op.drop_table('disc_data_search', schema='disc')
    op.drop_table('disc_market_track', schema='disc')
    
    # Drop schema (optional - comment out if you want to keep the schema)
    # op.execute(sa.text("DROP SCHEMA IF EXISTS disc"))
