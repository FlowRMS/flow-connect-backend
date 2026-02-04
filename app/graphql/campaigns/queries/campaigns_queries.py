from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.campaigns.services.campaign_email_sender_service import (
    CampaignEmailSenderService,
)
from app.graphql.campaigns.services.campaigns_service import CampaignsService
from app.graphql.campaigns.strawberry.campaign_recipient_response import (
    CampaignRecipientResponse,
)
from app.graphql.campaigns.strawberry.campaign_response import CampaignResponse
from app.graphql.campaigns.strawberry.campaign_sending_status_response import (
    CampaignSendingStatusResponse,
)
from app.graphql.campaigns.strawberry.criteria_input import CampaignCriteriaInput
from app.graphql.campaigns.strawberry.estimate_recipients_response import (
    EstimateRecipientsResponse,
)
from app.graphql.contacts.strawberry.contact_response import ContactResponse
from app.graphql.inject import inject


@strawberry.type
class CampaignsQueries:
    """GraphQL queries for Campaigns entity."""

    @strawberry.field
    @inject
    async def campaign(
        self,
        id: UUID,
        service: Injected[CampaignsService],
    ) -> CampaignResponse:
        """Get a campaign by ID with all details."""
        return CampaignResponse.from_orm_model(await service.get_campaign(id))

    @strawberry.field
    @inject
    async def campaign_recipients(
        self,
        campaign_id: UUID,
        service: Injected[CampaignsService],
        limit: int = 100,
        offset: int = 0,
    ) -> list[CampaignRecipientResponse]:
        """Get recipients for a campaign with pagination."""
        recipients = await service.get_campaign_recipients(campaign_id, limit, offset)
        return CampaignRecipientResponse.from_orm_model_list(recipients)

    @strawberry.field
    @inject
    async def estimate_recipients(
        self,
        criteria: CampaignCriteriaInput,
        service: Injected[CampaignsService],
        sample_limit: int = 10,
    ) -> EstimateRecipientsResponse:
        """Estimate the number of recipients for given criteria.

        Args:
            criteria: The criteria to evaluate
            service: Injected campaigns service
            sample_limit: Maximum number of sample contacts to return (default: 10)

        Returns:
            EstimateRecipientsResponse with count and list of sample contacts
        """
        count, sample_contacts = await service.estimate_recipients(
            criteria, sample_limit=sample_limit
        )
        return EstimateRecipientsResponse(
            count=count,
            sample_contacts=[
                ContactResponse.from_orm_model(contact) for contact in sample_contacts
            ],
        )

    @strawberry.field
    @inject
    async def campaign_sending_status(
        self,
        campaign_id: UUID,
        sender_service: Injected[CampaignEmailSenderService],
    ) -> CampaignSendingStatusResponse:
        """Get the current sending status of a campaign.

        Returns detailed information about:
        - Total recipients and counts by status (sent, pending, failed, bounced)
        - Today's sent count and remaining quota
        - Send pace configuration
        - Progress percentage and completion status
        """
        status = await sender_service.get_sending_status(campaign_id)
        return CampaignSendingStatusResponse.from_dataclass(status)
