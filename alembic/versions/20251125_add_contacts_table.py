"""add_contacts_table

Revision ID: b65a7d6cf2f2
Revises: be97a67210be
Create Date: 2025-11-25 14:02:25.240946

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'b65a7d6cf2f2'
down_revision: str | None = 'be97a67210be'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create contacts table
    _ = op.create_table(
        "contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "entry_date",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("role", sa.String(length=100), nullable=True),
        sa.Column("territory", sa.String(length=100), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["crm.companies.id"],
            name="fk_contacts_company_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="crm",
    )

    # Create indexes for contacts table
    op.create_index(
        "ix_crm_contacts_email", "contacts", ["email"], schema="crm"
    )
    op.create_index(
        "ix_crm_contacts_company_id", "contacts", ["company_id"], schema="crm"
    )
    op.create_index(
        "ix_crm_contacts_territory", "contacts", ["territory"], schema="crm"
    )
    op.create_index(
        "ix_crm_contacts_created_by", "contacts", ["created_by"], schema="crm"
    )
    op.create_index(
        "ix_crm_contacts_last_name", "contacts", ["last_name"], schema="crm"
    )


def downgrade() -> None:
    # Drop contacts table and its indexes
    op.drop_index("ix_crm_contacts_last_name", table_name="contacts", schema="crm")
    op.drop_index("ix_crm_contacts_created_by", table_name="contacts", schema="crm")
    op.drop_index("ix_crm_contacts_territory", table_name="contacts", schema="crm")
    op.drop_index("ix_crm_contacts_company_id", table_name="contacts", schema="crm")
    op.drop_index("ix_crm_contacts_email", table_name="contacts", schema="crm")
    op.drop_table("contacts", schema="crm")
