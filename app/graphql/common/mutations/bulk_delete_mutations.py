from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.common.bulk_delete_entity_type import BulkDeleteEntityType
from app.graphql.common.services.bulk_delete_service import BulkDeleteService
from app.graphql.common.strawberry.bulk_delete_response import BulkDeleteResult
from app.graphql.inject import inject


@strawberry.type
class BulkDeleteMutations:
    @strawberry.mutation
    @inject
    async def bulk_delete(
        self,
        entity_type: BulkDeleteEntityType,
        entity_ids: list[UUID],
        service: Injected[BulkDeleteService],
    ) -> BulkDeleteResult:
        return await service.delete_entities(entity_type, entity_ids)
