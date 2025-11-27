"""add_companies_table

Revision ID: be97a67210be
Revises: a1b2c3d4e5f6
Create Date: 2025-11-25 14:01:52.950106

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'be97a67210be'
down_revision: str | None = 'a1b2c3d4e5f6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create companies table
    _ = op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "entry_date",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("company_source_type", sa.SmallInteger(), nullable=False),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("parent_company_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="crm",
    )

    # Create indexes for companies table
    op.create_index(
        "ix_crm_companies_name", "companies", ["name"], schema="crm"
    )
    op.create_index(
        "ix_crm_companies_company_source_type", "companies", ["company_source_type"], schema="crm"
    )
    op.create_index(
        "ix_crm_companies_created_by", "companies", ["created_by"], schema="crm"
    )


def downgrade() -> None:
    # Drop companies table and its indexes
    op.drop_index("ix_crm_companies_created_by", table_name="companies", schema="crm")
    op.drop_index("ix_crm_companies_company_source_type", table_name="companies", schema="crm")
    op.drop_index("ix_crm_companies_name", table_name="companies", schema="crm")
    op.drop_table("companies", schema="crm")
