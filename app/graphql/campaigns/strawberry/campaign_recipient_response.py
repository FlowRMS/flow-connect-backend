from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.campaigns.campaign_recipient_model import CampaignRecipient
from commons.db.v6.crm.campaigns.email_status import EmailStatus

from app.core.db.adapters.dto import DTOMixin
from app.graphql.contacts.strawberry.contact_response import ContactResponse


@strawberry.type
class CampaignRecipientResponse(DTOMixin[CampaignRecipient]):
    """GraphQL type for CampaignRecipient entity."""

    id: UUID
    campaign_id: UUID
    contact_id: UUID
    email_status: EmailStatus
    sent_at: datetime | None
    personalized_content: str | None
    contact: ContactResponse

    @classmethod
    def from_orm_model(cls, model: CampaignRecipient) -> Self:
        return cls(
            id=model.id,
            campaign_id=model.campaign_id,
            contact_id=model.contact_id,
            email_status=model.email_status,
            sent_at=model.sent_at,
            personalized_content=model.personalized_content,
            contact=ContactResponse.from_orm_model(model.contact),
        )
