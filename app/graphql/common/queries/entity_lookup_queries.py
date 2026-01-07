from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.common.entity_source_type import EntitySourceType
from app.graphql.common.services.entity_lookup_service import EntityLookupService
from app.graphql.common.strawberry.entity_response import EntityResponse
from app.graphql.inject import inject


@strawberry.type
class EntityLookupQueries:
    @strawberry.field
    @inject
    async def entity(
        self,
        source_type: EntitySourceType,
        entity_id: UUID,
        service: Injected[EntityLookupService],
    ) -> EntityResponse:
        return await service.get_entity(source_type, entity_id)
