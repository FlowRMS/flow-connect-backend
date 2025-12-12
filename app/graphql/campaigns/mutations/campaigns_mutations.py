"""GraphQL mutations for Campaigns entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.campaigns.services.campaign_email_sender_service import (
    CampaignEmailSenderService,
)
from app.graphql.campaigns.services.campaigns_service import CampaignsService
from app.graphql.campaigns.strawberry.campaign_input import CampaignInput
from app.graphql.campaigns.strawberry.campaign_response import CampaignResponse
from app.graphql.campaigns.strawberry.campaign_sending_status_response import (
    SendTestEmailResponse,
)
from app.graphql.inject import inject


@strawberry.type
class CampaignsMutations:
    """GraphQL mutations for Campaigns entity."""

    @strawberry.mutation
    @inject
    async def create_campaign(
        self,
        input: CampaignInput,
        service: Injected[CampaignsService],
    ) -> CampaignResponse:
        """Create a new campaign with recipients."""
        return CampaignResponse.from_orm_model(
            await service.create_campaign(campaign_input=input)
        )

    @strawberry.mutation
    @inject
    async def update_campaign(
        self,
        id: UUID,
        input: CampaignInput,
        service: Injected[CampaignsService],
    ) -> CampaignResponse:
        """Update an existing campaign."""
        return CampaignResponse.from_orm_model(await service.update_campaign(id, input))

    @strawberry.mutation
    @inject
    async def delete_campaign(
        self,
        id: UUID,
        service: Injected[CampaignsService],
    ) -> bool:
        """Delete a campaign and all its recipients."""
        return await service.delete_campaign(campaign_id=id)

    @strawberry.mutation
    @inject
    async def pause_campaign(
        self,
        id: UUID,
        service: Injected[CampaignsService],
    ) -> CampaignResponse:
        """Pause a campaign that is currently sending."""
        return CampaignResponse.from_orm_model(
            await service.pause_campaign(campaign_id=id)
        )

    @strawberry.mutation
    @inject
    async def resume_campaign(
        self,
        id: UUID,
        service: Injected[CampaignsService],
    ) -> CampaignResponse:
        """Resume a paused campaign."""
        return CampaignResponse.from_orm_model(
            await service.resume_campaign(campaign_id=id)
        )

    @strawberry.mutation
    @inject
    async def refresh_dynamic_recipients(
        self,
        campaign_id: UUID,
        service: Injected[CampaignsService],
    ) -> CampaignResponse:
        """Refresh recipients for a dynamic campaign based on its criteria."""
        return CampaignResponse.from_orm_model(
            await service.refresh_dynamic_recipients(campaign_id)
        )

    @strawberry.mutation
    @inject
    async def send_test_email(
        self,
        campaign_id: UUID,
        test_email: str,
        sender_service: Injected[CampaignEmailSenderService],
    ) -> SendTestEmailResponse:
        """Send a test email for a campaign to a specific email address."""
        result = await sender_service.send_test_email(campaign_id, test_email)
        return SendTestEmailResponse(
            success=result.emails_sent > 0,
            error=result.errors[0] if result.errors else None,
        )

    @strawberry.mutation
    @inject
    async def start_campaign_sending(
        self,
        campaign_id: UUID,
        sender_service: Injected[CampaignEmailSenderService],
    ) -> CampaignResponse:
        """Start sending a campaign.

        Sets the campaign status to SENDING. The background worker will
        automatically pick it up and process emails respecting pace and daily limits.

        Use pauseCampaign to stop sending.
        """
        campaign = await sender_service.start_campaign(campaign_id)
        return CampaignResponse.from_orm_model(campaign)
