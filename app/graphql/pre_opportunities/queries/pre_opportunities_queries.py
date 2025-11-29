"""GraphQL queries for PreOpportunity entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_response import (
    PreOpportunityResponse,
)


@strawberry.type
class PreOpportunitiesQueries:
    """GraphQL queries for PreOpportunity entity."""

    @strawberry.field
    @inject
    async def pre_opportunity(
        self,
        id: UUID,
        service: Injected[PreOpportunitiesService],
    ) -> PreOpportunityResponse:
        """Get a pre-opportunity by ID."""
        pre_opportunity = await service.get_pre_opportunity(id)
        return PreOpportunityResponse.from_orm_model(pre_opportunity)
