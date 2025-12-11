"""add campaign_send_logs table

Revision ID: c4mp41gn5002
Revises: c4mp41gn5001
Create Date: 2025-12-11 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "c4mp41gn5002"
down_revision: str | None = "c4mp41gn5001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create campaign_send_logs table for tracking daily email counts
    op.create_table(
        "campaign_send_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("send_date", sa.Date(), nullable=False),
        sa.Column("emails_sent", sa.Integer(), nullable=False, default=0),
        sa.Column("last_sent_at", postgresql.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["campaign_id"],
            ["pycrm.campaigns.id"],
            name="fk_campaign_send_logs_campaign_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "send_date", name="uq_campaign_send_date"),
        schema="pycrm",
    )

    # Create indexes for efficient queries
    op.create_index(
        "ix_campaign_send_logs_campaign_id",
        "campaign_send_logs",
        ["campaign_id"],
        schema="pycrm",
    )
    op.create_index(
        "ix_campaign_send_logs_send_date",
        "campaign_send_logs",
        ["send_date"],
        schema="pycrm",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_campaign_send_logs_send_date",
        table_name="campaign_send_logs",
        schema="pycrm",
    )
    op.drop_index(
        "ix_campaign_send_logs_campaign_id",
        table_name="campaign_send_logs",
        schema="pycrm",
    )
    op.drop_table("campaign_send_logs", schema="pycrm")
