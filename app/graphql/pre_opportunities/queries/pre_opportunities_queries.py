from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_lite_response import (
    PreOpportunityLiteResponse,
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

    @strawberry.field
    @inject
    async def pre_opportunity_search(
        self,
        service: Injected[PreOpportunitiesService],
        search_term: str,
        limit: int = 20,
    ) -> list[PreOpportunityLiteResponse]:
        """
        Search pre-opportunities by entity number.

        Args:
            search_term: The search term to match against entity number
            limit: Maximum number of pre-opportunities to return (default: 20)

        Returns:
            List of PreOpportunityLiteResponse objects matching the search criteria
        """
        return PreOpportunityLiteResponse.from_orm_model_list(
            await service.search_pre_opportunities(search_term, limit)
        )
