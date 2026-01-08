from typing import override
from uuid import UUID

from app.graphql.common.entity_source_type import EntitySourceType
from app.graphql.common.interfaces.entity_lookup_strategy import EntityLookupStrategy
from app.graphql.common.strawberry.entity_response import EntityResponse
from app.graphql.pre_opportunities.services.pre_opportunities_service import (
    PreOpportunitiesService,
)
from app.graphql.pre_opportunities.strawberry.pre_opportunity_response import (
    PreOpportunityResponse,
)


class PreOpportunityEntityStrategy(EntityLookupStrategy):
    def __init__(self, service: PreOpportunitiesService) -> None:
        super().__init__()
        self.service = service

    @override
    def get_supported_source_type(self) -> EntitySourceType:
        return EntitySourceType.PRE_OPPORTUNITIES

    @override
    async def get_entity(self, entity_id: UUID) -> EntityResponse:
        pre_opportunity = await self.service.get_pre_opportunity(entity_id)
        return PreOpportunityResponse.from_orm_model(pre_opportunity)
