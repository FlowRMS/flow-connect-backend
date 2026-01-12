"""add job_company_links table

Revision ID: add_job_company_links
Revises: a345ab2dcc2e
Create Date: 2026-01-12

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "add_job_company_links"
down_revision: str | None = "a345ab2dcc2e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "job_company_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "job_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycrm.jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "company_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycrm.companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "created_by_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pycrm.users.id"),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "job_id", "company_id", "role", name="uq_job_company_links_job_company_role"
        ),
        schema="pycrm",
    )
    op.create_index(
        "ix_job_company_links_job_id",
        "job_company_links",
        ["job_id"],
        schema="pycrm",
    )
    op.create_index(
        "ix_job_company_links_company_id",
        "job_company_links",
        ["company_id"],
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_job_company_links_company_id",
        table_name="job_company_links",
        schema="pycrm",
    )
    op.drop_index(
        "ix_job_company_links_job_id",
        table_name="job_company_links",
        schema="pycrm",
    )
    op.drop_table("job_company_links", schema="pycrm")
