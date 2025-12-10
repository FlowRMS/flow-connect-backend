"""SQLAlchemy ORM model for CampaignRecipient entity."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from commons.db.int_enum import IntEnum
from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel
from app.graphql.campaigns.models.email_status import EmailStatus

if TYPE_CHECKING:
    from app.graphql.campaigns.models.campaign_model import Campaign
    from app.graphql.contacts.models.contact_model import Contact


class CampaignRecipient(CrmBaseModel, kw_only=True):
    """Campaign recipient entity linking campaigns to contacts."""

    __tablename__ = "campaign_recipients"

    # Required fields without defaults
    campaign_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pycrm.campaigns.id", ondelete="CASCADE"),
        nullable=False,
    )
    contact_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pycrm.contacts.id"),
        nullable=False,
    )
    email_status: Mapped[EmailStatus] = mapped_column(
        IntEnum(EmailStatus), nullable=False
    )

    # Optional fields with defaults
    sent_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True, default=None
    )
    personalized_content: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None
    )

    campaign: Mapped["Campaign"] = relationship(init=False, back_populates="recipients")
    contact: Mapped["Contact"] = relationship(init=False, lazy="joined")
