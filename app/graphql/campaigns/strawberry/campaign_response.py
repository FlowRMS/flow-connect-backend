"""GraphQL response type for Campaign entity."""

from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from app.graphql.campaigns.models.campaign_model import Campaign
from app.graphql.campaigns.models.campaign_status import CampaignStatus
from app.graphql.campaigns.models.email_status import EmailStatus
from app.graphql.campaigns.models.recipient_list_type import RecipientListType
from app.graphql.campaigns.models.send_pace import SendPace


@strawberry.type
class CampaignResponse(DTOMixin[Campaign]):
    """GraphQL type for Campaign entity (output/query results)."""

    id: UUID
    created_at: datetime
    name: str
    status: CampaignStatus
    recipient_list_type: RecipientListType
    description: str | None
    email_subject: str | None
    email_body: str | None
    ai_personalization_enabled: bool
    send_pace: SendPace
    max_emails_per_day: int | None
    scheduled_at: datetime | None
    send_immediately: bool
    recipients_count: int
    sent_count: int
    criteria_json: strawberry.scalars.JSON | None

    @classmethod
    def from_orm_model(cls, model: Campaign) -> Self:
        sent_count = (
            sum(1 for r in model.recipients if r.email_status == EmailStatus.SENT)
            if model.recipients
            else 0
        )

        return cls(
            id=model.id,
            created_at=model.created_at,
            name=model.name,
            status=model.status,
            recipient_list_type=model.recipient_list_type,
            description=model.description,
            email_subject=model.email_subject,
            email_body=model.email_body,
            ai_personalization_enabled=model.ai_personalization_enabled or False,
            send_pace=model.send_pace or SendPace.MEDIUM,
            max_emails_per_day=model.max_emails_per_day,
            scheduled_at=model.scheduled_at,
            send_immediately=model.send_immediately or False,
            recipients_count=len(model.recipients) if model.recipients else 0,
            sent_count=sent_count,
            criteria_json=model.criteria.criteria_json if model.criteria else None,
        )
