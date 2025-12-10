"""SQLAlchemy ORM model for Campaign entity."""

from datetime import datetime
from typing import TYPE_CHECKING

from commons.db.int_enum import IntEnum
from commons.db.models import User
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel, HasCreatedAt, HasCreatedBy
from app.graphql.campaigns.models.campaign_status import CampaignStatus
from app.graphql.campaigns.models.recipient_list_type import RecipientListType
from app.graphql.campaigns.models.send_pace import SendPace

if TYPE_CHECKING:
    from app.graphql.campaigns.models.campaign_criteria_model import CampaignCriteria
    from app.graphql.campaigns.models.campaign_recipient_model import CampaignRecipient


class Campaign(CrmBaseModel, HasCreatedAt, HasCreatedBy, kw_only=True):
    """Campaign entity representing an email campaign in the CRM system."""

    __tablename__ = "campaigns"

    # Required fields (no defaults) - must come first
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    recipient_list_type: Mapped[RecipientListType] = mapped_column(
        IntEnum(RecipientListType), nullable=False
    )
    status: Mapped[CampaignStatus] = mapped_column(
        IntEnum(CampaignStatus), nullable=False
    )

    # Optional fields with defaults
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    email_subject: Mapped[str | None] = mapped_column(
        String(500), nullable=True, default=None
    )
    email_body: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    ai_personalization_enabled: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, default=None
    )
    send_pace: Mapped[SendPace | None] = mapped_column(
        IntEnum(SendPace), nullable=True, default=None
    )
    max_emails_per_day: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None
    )
    send_immediately: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True, default=None
    )

    created_by: Mapped[User] = relationship(init=False, lazy="joined")
    recipients: Mapped[list["CampaignRecipient"]] = relationship(
        init=False, back_populates="campaign", cascade="all, delete-orphan"
    )
    criteria: Mapped["CampaignCriteria | None"] = relationship(
        init=False, back_populates="campaign", cascade="all, delete-orphan", uselist=False
    )
