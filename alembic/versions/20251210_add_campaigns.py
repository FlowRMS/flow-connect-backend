"""add campaigns tables

Revision ID: c4mp41gn5001
Revises: c4b9f784a484
Create Date: 2025-12-10 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c4mp41gn5001"
down_revision: str | None = "c4b9f784a484"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create campaigns table
    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.Integer(), nullable=False, default=1),
        sa.Column("recipient_list_type", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("email_subject", sa.String(length=500), nullable=True),
        sa.Column("email_body", sa.Text(), nullable=True),
        sa.Column("ai_personalization_enabled", sa.Boolean(), nullable=False, default=False),
        sa.Column("send_pace", sa.Integer(), nullable=False, default=2),
        sa.Column("max_emails_per_day", sa.Integer(), nullable=True),
        sa.Column("scheduled_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("send_immediately", sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )

    # Create campaign_recipients table
    op.create_table(
        "campaign_recipients",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email_status", sa.Integer(), nullable=False, default=1),
        sa.Column("sent_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("personalized_content", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["pycrm.campaigns.id"],
            name="fk_campaign_recipients_campaign_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["contact_id"],
            ["pycrm.contacts.id"],
            name="fk_campaign_recipients_contact_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )

    # Create campaign_criteria table
    op.create_table(
        "campaign_criteria",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column("criteria_json", postgresql.JSONB(), nullable=False),
        sa.Column("is_dynamic", sa.Boolean(), nullable=False, default=False),
        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["pycrm.campaigns.id"],
            name="fk_campaign_criteria_campaign_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="pycrm",
    )

    # Create indexes
    op.create_index(
        "ix_campaigns_status",
        "campaigns",
        ["status"],
        schema="pycrm",
    )
    op.create_index(
        "ix_campaign_recipients_campaign_id",
        "campaign_recipients",
        ["campaign_id"],
        schema="pycrm",
    )
    op.create_index(
        "ix_campaign_recipients_contact_id",
        "campaign_recipients",
        ["contact_id"],
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_index("ix_campaign_recipients_contact_id", table_name="campaign_recipients", schema="pycrm")
    op.drop_index("ix_campaign_recipients_campaign_id", table_name="campaign_recipients", schema="pycrm")
    op.drop_index("ix_campaigns_status", table_name="campaigns", schema="pycrm")
    op.drop_table("campaign_criteria", schema="pycrm")
    op.drop_table("campaign_recipients", schema="pycrm")
    op.drop_table("campaigns", schema="pycrm")
