"""add_addresses_table

Revision ID: 0ecc4ba6a0e8
Revises: b65a7d6cf2f2
Create Date: 2025-11-26 19:17:45.812891

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0ecc4ba6a0e8'
down_revision: str | None = 'b65a7d6cf2f2'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create addresses table
    _ = op.create_table(
        "addresses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "entry_date",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("address_type", sa.SmallInteger(), nullable=False),
        sa.Column("address_line_1", sa.String(length=255), nullable=True),
        sa.Column("address_line_2", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("zip_code", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["crm.companies.id"],
            name="fk_addresses_company_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="crm",
    )

    # Create indexes for addresses table
    op.create_index(
        "ix_crm_addresses_company_id", "addresses", ["company_id"], schema="crm"
    )
    op.create_index(
        "ix_crm_addresses_address_type", "addresses", ["address_type"], schema="crm"
    )
    op.create_index(
        "ix_crm_addresses_created_by", "addresses", ["created_by"], schema="crm"
    )


def downgrade() -> None:
    # Drop addresses table and its indexes
    op.drop_index("ix_crm_addresses_created_by", table_name="addresses", schema="crm")
    op.drop_index("ix_crm_addresses_address_type", table_name="addresses", schema="crm")
    op.drop_index("ix_crm_addresses_company_id", table_name="addresses", schema="crm")
    op.drop_table("addresses", schema="crm")
