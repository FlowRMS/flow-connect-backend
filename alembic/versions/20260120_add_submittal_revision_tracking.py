# add submittal revision tracking tables
# Revision ID: add_submittal_revision_tracking
# Revises: 2adbedfe0eff
# Create Date: 2026-01-20
# Adds tables for tracking:
# - Returned PDFs (from engineers/architects)
# - Change analysis (AI or manual)
# - Item-level changes

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_submittal_revision_tracking"
down_revision: str | None = "2adbedfe0eff"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names(schema="pycrm")

    # Skip if tables already exist (idempotent migration)
    if "submittal_returned_pdfs" in tables:
        return

    # Create submittal_returned_pdfs table
    op.create_table(
        "submittal_returned_pdfs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("revision_id", sa.UUID(), nullable=False),
        sa.Column("returned_by_stakeholder_id", sa.UUID(), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("received_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["revision_id"],
            ["pycrm.submittal_revisions.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["returned_by_stakeholder_id"],
            ["pycrm.submittal_stakeholders.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["created_by_id"], ["pyuser.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )
    op.create_index(
        "ix_pycrm_submittal_returned_pdfs_revision_id",
        "submittal_returned_pdfs",
        ["revision_id"],
        schema="pycrm",
    )

    # Create submittal_change_analyses table
    op.create_table(
        "submittal_change_analyses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("returned_pdf_id", sa.UUID(), nullable=False),
        sa.Column(
            "analyzed_by", sa.Integer(), nullable=False, server_default="1"
        ),  # 0=AI, 1=MANUAL
        sa.Column(
            "overall_status", sa.Integer(), nullable=False, server_default="0"
        ),  # 0=APPROVED
        sa.Column(
            "total_changes_detected", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["returned_pdf_id"],
            ["pycrm.submittal_returned_pdfs.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("returned_pdf_id"),
        schema="pycrm",
    )
    op.create_index(
        "ix_pycrm_submittal_change_analyses_returned_pdf_id",
        "submittal_change_analyses",
        ["returned_pdf_id"],
        unique=True,
        schema="pycrm",
    )

    # Create submittal_item_changes table
    op.create_table(
        "submittal_item_changes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("change_analysis_id", sa.UUID(), nullable=False),
        sa.Column("item_id", sa.UUID(), nullable=True),
        sa.Column("fixture_type", sa.String(length=50), nullable=False),
        sa.Column("catalog_number", sa.String(length=255), nullable=False),
        sa.Column("manufacturer", sa.String(length=255), nullable=False),
        sa.Column(
            "status", sa.Integer(), nullable=False, server_default="0"
        ),  # 0=APPROVED
        sa.Column("notes", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("page_references", postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["change_analysis_id"],
            ["pycrm.submittal_change_analyses.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["item_id"],
            ["pycrm.submittal_items.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )
    op.create_index(
        "ix_pycrm_submittal_item_changes_change_analysis_id",
        "submittal_item_changes",
        ["change_analysis_id"],
        schema="pycrm",
    )
    op.create_index(
        "ix_pycrm_submittal_item_changes_item_id",
        "submittal_item_changes",
        ["item_id"],
        schema="pycrm",
    )


def downgrade() -> None:
    # Drop tables in reverse order due to foreign key constraints
    op.drop_index(
        "ix_pycrm_submittal_item_changes_item_id",
        table_name="submittal_item_changes",
        schema="pycrm",
    )
    op.drop_index(
        "ix_pycrm_submittal_item_changes_change_analysis_id",
        table_name="submittal_item_changes",
        schema="pycrm",
    )
    op.drop_table("submittal_item_changes", schema="pycrm")

    op.drop_index(
        "ix_pycrm_submittal_change_analyses_returned_pdf_id",
        table_name="submittal_change_analyses",
        schema="pycrm",
    )
    op.drop_table("submittal_change_analyses", schema="pycrm")

    op.drop_index(
        "ix_pycrm_submittal_returned_pdfs_revision_id",
        table_name="submittal_returned_pdfs",
        schema="pycrm",
    )
    op.drop_table("submittal_returned_pdfs", schema="pycrm")
