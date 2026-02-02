from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "submittals_001"
down_revision: str | None = "3788145070d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create submittals table (with all config fields included)
    _ = op.create_table(
        "submittals",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submittal_number", sa.String(length=50), nullable=False),
        sa.Column("quote_id", sa.UUID(), nullable=True),
        sa.Column("job_id", sa.UUID(), nullable=True),
        sa.Column(
            "status", sa.Integer(), nullable=False, server_default="1"
        ),  # DRAFT=1
        sa.Column("transmittal_purpose", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Settings fields
        sa.Column("job_location", sa.Text(), nullable=True),
        sa.Column("bid_date", sa.Date(), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.Text()), nullable=True),
        # Config fields
        sa.Column(
            "config_include_lamps",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "config_include_accessories",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "config_include_cq",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "config_include_from_orders",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "config_roll_up_kits",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "config_roll_up_accessories",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "config_include_zero_quantity_items",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "config_drop_descriptions",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "config_drop_line_notes",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.ForeignKeyConstraint(["quote_id"], ["pycrm.quotes.id"]),
        sa.ForeignKeyConstraint(["job_id"], ["pycrm.jobs.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["pyuser.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )
    op.create_index(
        "ix_pycrm_submittals_quote_id",
        "submittals",
        ["quote_id"],
        schema="pycrm",
    )
    op.create_index(
        "ix_pycrm_submittals_job_id",
        "submittals",
        ["job_id"],
        schema="pycrm",
    )
    op.create_index(
        "ix_pycrm_submittals_submittal_number",
        "submittals",
        ["submittal_number"],
        schema="pycrm",
    )

    # Create submittal_items table (with manufacturer, lead_time)
    _ = op.create_table(
        "submittal_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submittal_id", sa.UUID(), nullable=False),
        sa.Column("item_number", sa.Integer(), nullable=False),
        sa.Column("quote_detail_id", sa.UUID(), nullable=True),
        sa.Column("spec_sheet_id", sa.UUID(), nullable=True),
        sa.Column("highlight_version_id", sa.UUID(), nullable=True),
        sa.Column("part_number", sa.String(length=100), nullable=True),
        sa.Column("manufacturer", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=18, scale=6), nullable=True),
        sa.Column(
            "approval_status", sa.Integer(), nullable=False, server_default="1"
        ),  # PENDING=1
        sa.Column(
            "match_status", sa.Integer(), nullable=False, server_default="1"
        ),  # NO_MATCH=1
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("lead_time", sa.String(100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["submittal_id"],
            ["pycrm.submittals.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["quote_detail_id"], ["pycrm.quote_details.id"]),
        sa.ForeignKeyConstraint(["spec_sheet_id"], ["pycrm.spec_sheets.id"]),
        sa.ForeignKeyConstraint(
            ["highlight_version_id"], ["pycrm.spec_sheet_highlight_versions.id"]
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )
    op.create_index(
        "ix_pycrm_submittal_items_submittal_id",
        "submittal_items",
        ["submittal_id"],
        schema="pycrm",
    )

    # Create submittal_stakeholders table
    _ = op.create_table(
        "submittal_stakeholders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submittal_id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=True),
        sa.Column(
            "role", sa.Integer(), nullable=False, server_default="1"
        ),  # CUSTOMER=1
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("contact_name", sa.String(length=255), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("contact_phone", sa.String(length=50), nullable=True),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["submittal_id"],
            ["pycrm.submittals.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["pycore.customers.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )
    op.create_index(
        "ix_pycrm_submittal_stakeholders_submittal_id",
        "submittal_stakeholders",
        ["submittal_id"],
        schema="pycrm",
    )

    # Create submittal_revisions table
    _ = op.create_table(
        "submittal_revisions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submittal_id", sa.UUID(), nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pdf_file_id", sa.UUID(), nullable=True),
        sa.Column("pdf_file_url", sa.Text(), nullable=True),
        sa.Column("pdf_file_name", sa.String(length=255), nullable=True),
        sa.Column("pdf_file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["submittal_id"],
            ["pycrm.submittals.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["created_by_id"], ["pyuser.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )
    op.create_index(
        "ix_pycrm_submittal_revisions_submittal_id",
        "submittal_revisions",
        ["submittal_id"],
        schema="pycrm",
    )

    # Create submittal_emails table
    _ = op.create_table(
        "submittal_emails",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("submittal_id", sa.UUID(), nullable=False),
        sa.Column("revision_id", sa.UUID(), nullable=True),
        sa.Column("subject", sa.String(length=500), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("recipients", postgresql.JSONB(), nullable=True),
        sa.Column("recipient_emails", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["submittal_id"],
            ["pycrm.submittals.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["revision_id"], ["pycrm.submittal_revisions.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["pyuser.users.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )
    op.create_index(
        "ix_pycrm_submittal_emails_submittal_id",
        "submittal_emails",
        ["submittal_id"],
        schema="pycrm",
    )

    # Create submittal_returned_pdfs table
    _ = op.create_table(
        "submittal_returned_pdfs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("revision_id", sa.UUID(), nullable=False),
        sa.Column("returned_by_stakeholder_id", sa.UUID(), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_url", sa.Text(), nullable=False),
        sa.Column(
            "file_id", sa.UUID(), nullable=True
        ),  # Reference to files table for presigned URLs
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
    _ = op.create_table(
        "submittal_change_analyses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("returned_pdf_id", sa.UUID(), nullable=False),
        sa.Column(
            "analyzed_by", sa.Integer(), nullable=False, server_default="1"
        ),  # 1=AI, 2=MANUAL
        sa.Column(
            "overall_status", sa.Integer(), nullable=False, server_default="1"
        ),  # 1=APPROVED
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
    _ = op.create_table(
        "submittal_item_changes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("change_analysis_id", sa.UUID(), nullable=False),
        sa.Column("item_id", sa.UUID(), nullable=True),
        sa.Column("fixture_type", sa.String(length=50), nullable=False),
        sa.Column("catalog_number", sa.String(length=255), nullable=False),
        sa.Column("manufacturer", sa.String(length=255), nullable=False),
        sa.Column(
            "status", sa.Integer(), nullable=False, server_default="1"
        ),  # 1=APPROVED
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

    op.drop_index(
        "ix_pycrm_submittal_emails_submittal_id",
        table_name="submittal_emails",
        schema="pycrm",
    )
    op.drop_table("submittal_emails", schema="pycrm")

    op.drop_index(
        "ix_pycrm_submittal_revisions_submittal_id",
        table_name="submittal_revisions",
        schema="pycrm",
    )
    op.drop_table("submittal_revisions", schema="pycrm")

    op.drop_index(
        "ix_pycrm_submittal_stakeholders_submittal_id",
        table_name="submittal_stakeholders",
        schema="pycrm",
    )
    op.drop_table("submittal_stakeholders", schema="pycrm")

    op.drop_index(
        "ix_pycrm_submittal_items_submittal_id",
        table_name="submittal_items",
        schema="pycrm",
    )
    op.drop_table("submittal_items", schema="pycrm")

    op.drop_index(
        "ix_pycrm_submittals_submittal_number",
        table_name="submittals",
        schema="pycrm",
    )
    op.drop_index(
        "ix_pycrm_submittals_job_id",
        table_name="submittals",
        schema="pycrm",
    )
    op.drop_index(
        "ix_pycrm_submittals_quote_id",
        table_name="submittals",
        schema="pycrm",
    )
    op.drop_table("submittals", schema="pycrm")
