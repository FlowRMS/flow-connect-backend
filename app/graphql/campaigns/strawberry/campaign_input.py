"""GraphQL input type for Campaign entity."""

from datetime import datetime
from uuid import UUID

import strawberry
from commons.db.v6.crm.campaigns.campaign_model import Campaign
from commons.db.v6.crm.campaigns.campaign_status import CampaignStatus
from commons.db.v6.crm.campaigns.recipient_list_type import RecipientListType
from commons.db.v6.crm.campaigns.send_pace import SendPace

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.campaigns.strawberry.criteria_input import CampaignCriteriaInput


@strawberry.input
class CampaignInput(BaseInputGQL[Campaign]):
    """GraphQL input type for creating/updating campaigns."""

    name: str
    recipient_list_type: RecipientListType
    description: str | None = strawberry.UNSET
    email_subject: str | None = strawberry.UNSET
    email_body: str | None = strawberry.UNSET
    ai_personalization_enabled: bool = False
    send_pace: SendPace = SendPace.MEDIUM
    max_emails_per_day: int | None = strawberry.UNSET
    scheduled_at: datetime | None = strawberry.UNSET
    send_immediately: bool = False
    static_contact_ids: list[UUID] | None = strawberry.UNSET
    criteria: CampaignCriteriaInput | None = strawberry.UNSET

    def _derive_status(self) -> CampaignStatus:
        """Derive campaign status from input fields.

        Status is determined by:
        - send_immediately=True → SENDING
        - scheduled_at is set → SCHEDULED
        - Otherwise → DRAFT
        """
        if self.send_immediately:
            return CampaignStatus.SENDING
        if self.scheduled_at and self.scheduled_at != strawberry.UNSET:
            return CampaignStatus.SCHEDULED
        return CampaignStatus.DRAFT

    def to_orm_model(self) -> Campaign:
        """Convert input to ORM model with derived status."""
        return Campaign(
            name=self.name,
            recipient_list_type=self.recipient_list_type,
            status=self._derive_status(),
            description=self.optional_field(self.description),
            email_subject=self.optional_field(self.email_subject),
            email_body=self.optional_field(self.email_body),
            ai_personalization_enabled=self.ai_personalization_enabled,
            send_pace=self.send_pace,
            max_emails_per_day=self.optional_field(self.max_emails_per_day),
            scheduled_at=self.optional_field(self.scheduled_at),  # pyright: ignore[reportArgumentType]
            send_immediately=self.send_immediately,
        )
