"""initial commit

Revision ID: 87005d4e17a7
Revises: 
Create Date: 2025-11-24 14:56:52.817766

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '87005d4e17a7'
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS crm")
    _ = op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entry_date", postgresql.TIMESTAMP(), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.SmallInteger(), nullable=False),
        sa.Column("job_name", sa.String(length=255), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("requester_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("job_owner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("job_name"),
        schema="crm"
    )

    op.create_index("ix_crm_jobs_job_owner_id", "jobs", ["job_owner_id"], schema="crm")
    op.create_index("ix_crm_jobs_created_by", "jobs", ["created_by"], schema="crm")
    op.create_index("ix_crm_jobs_start_date", "jobs", ["start_date"], schema="crm")
    op.create_index("ix_crm_jobs_end_date", "jobs", ["end_date"], schema="crm")

def downgrade() -> None:
    op.drop_index("ix_crm_jobs_end_date", table_name="jobs", schema="crm")
    op.drop_index("ix_crm_jobs_start_date", table_name="jobs", schema="crm")
    op.drop_index("ix_crm_jobs_created_by", table_name="jobs", schema="crm")
    op.drop_index("ix_crm_jobs_job_owner_id", table_name="jobs", schema="crm")
    op.drop_index("ix_crm_jobs_status", table_name="jobs", schema="crm")
    op.drop_table("jobs", schema="crm")