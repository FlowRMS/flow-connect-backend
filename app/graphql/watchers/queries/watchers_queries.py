from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.inject import inject
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.watchers.services.entity_watcher_service import EntityWatcherService


@strawberry.type
class WatchersQueries:
    @strawberry.field
    @inject
    async def get_watchers_by_entity(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        watcher_service: Injected[EntityWatcherService],
    ) -> list[UserResponse]:
        users = await watcher_service.get_watchers(entity_type, entity_id)
        return [UserResponse.from_orm_model(u) for u in users]
