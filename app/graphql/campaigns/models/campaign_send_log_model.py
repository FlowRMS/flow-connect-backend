"""SQLAlchemy ORM model for CampaignSendLog entity."""

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import CrmBaseModel, HasCreatedAt


class CampaignSendLog(CrmBaseModel, HasCreatedAt, kw_only=True):
    """
    Tracks daily email sending counts per campaign.

    Used to enforce max_emails_per_day limits and track sending progress.
    """

    __tablename__ = "campaign_send_logs"
    __table_args__ = (
        UniqueConstraint("campaign_id", "send_date", name="uq_campaign_send_date"),
        {"schema": "pycrm"},
    )

    campaign_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pycrm.campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    send_date: Mapped[date] = mapped_column(Date, nullable=False)
    emails_sent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_sent_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None
    )
