from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.common.landing_source_type import LandingSourceType
from app.graphql.common.services.related_entities_service import RelatedEntitiesService
from app.graphql.common.strawberry.related_entities_response import (
    RelatedEntitiesResponse,
)
from app.graphql.inject import inject


@strawberry.type
class RelatedEntitiesQueries:
    @strawberry.field
    @inject
    async def related_entities(
        self,
        source_type: LandingSourceType,
        entity_id: UUID,
        service: Injected[RelatedEntitiesService],
    ) -> RelatedEntitiesResponse:
        return await service.get_related_entities(source_type, entity_id)
