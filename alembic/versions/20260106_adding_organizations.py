"""adding organizations table

Revision ID: organizations_001
Revises: pending_doc_proc_001
Create Date: 2026-01-06

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "organizations_001"
down_revision: str | None = "pending_doc_proc_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _ = op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("street_address", sa.String(500), nullable=False),
        sa.Column("address_line_2", sa.String(500), nullable=True),
        sa.Column("city", sa.String(255), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("zip_code", sa.String(20), nullable=False),
        sa.Column("email_address", sa.String(255), nullable=False),
        sa.Column("phone_number", sa.String(50), nullable=False),
        sa.Column(
            "logo_file_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("pyfiles.files.id"),
            nullable=True,
        ),
        sa.Column("logo_width", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("logo_height", sa.Integer(), nullable=False, server_default="100"),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        schema="pycore",
    )


def downgrade() -> None:
    op.drop_table("organizations", schema="pycore")
