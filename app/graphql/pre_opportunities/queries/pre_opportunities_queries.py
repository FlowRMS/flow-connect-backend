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

    @strawberry.field
    @inject
    async def pre_opportunities_by_job(
        self,
        job_id: UUID,
        service: Injected[PreOpportunitiesService],
    ) -> list[PreOpportunityResponse]:
        """Get all pre-opportunities for a specific job."""
        pre_opportunities = await service.get_by_job_id(job_id)
        return PreOpportunityResponse.from_orm_model_list(pre_opportunities)

    @strawberry.field
    @inject
    async def pre_opportunities_by_customer(
        self,
        customer_id: UUID,
        service: Injected[PreOpportunitiesService],
    ) -> list[PreOpportunityResponse]:
        """Get all pre-opportunities for a specific customer."""
        pre_opportunities = await service.get_by_customer_id(customer_id)
        return PreOpportunityResponse.from_orm_model_list(pre_opportunities)
