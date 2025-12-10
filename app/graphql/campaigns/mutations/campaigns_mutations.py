"""GraphQL mutations for Campaigns entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.campaigns.services.campaigns_service import CampaignsService
from app.graphql.campaigns.strawberry.campaign_input import CampaignInput
from app.graphql.campaigns.strawberry.campaign_response import CampaignResponse
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
        return CampaignResponse.from_orm_model(await service.pause_campaign(campaign_id=id))

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
        service: Injected[CampaignsService],
    ) -> bool:
        """Send a test email for a campaign (placeholder for email service integration)."""
        await service.get_campaign(campaign_id)
        return True
