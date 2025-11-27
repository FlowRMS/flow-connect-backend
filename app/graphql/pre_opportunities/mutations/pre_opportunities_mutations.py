"""GraphQL mutations for PreOpportunity entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_input import (
    PreOpportunityInput,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_response import (
    PreOpportunityResponse,
)


@strawberry.type
class PreOpportunitiesMutations:
    """GraphQL mutations for PreOpportunity entity."""

    @strawberry.mutation
    @inject
    async def create_pre_opportunity(
        self,
        input: PreOpportunityInput,
        service: Injected[PreOpportunitiesService],
    ) -> PreOpportunityResponse:
        """Create a new pre-opportunity."""
        pre_opportunity = await service.create_pre_opportunity(
            pre_opportunity_input=input
        )
        return PreOpportunityResponse.from_orm_model(pre_opportunity)

    @strawberry.mutation
    @inject
    async def update_pre_opportunity(
        self,
        input: PreOpportunityInput,
        service: Injected[PreOpportunitiesService],
    ) -> PreOpportunityResponse:
        """Update a pre-opportunity."""
        pre_opportunity = await service.update_pre_opportunity(
            pre_opportunity_input=input
        )
        return PreOpportunityResponse.from_orm_model(pre_opportunity)

    @strawberry.mutation
    @inject
    async def delete_pre_opportunity(
        self,
        id: UUID,
        service: Injected[PreOpportunitiesService],
    ) -> bool:
        """Delete a pre-opportunity by ID."""
        return await service.delete_pre_opportunity(pre_opportunity_id=id)
