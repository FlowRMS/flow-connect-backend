from uuid import UUID

from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.user import User

from app.errors.common_errors import ConflictError, NotFoundError
from app.graphql.watchers.repositories.entity_watcher_repository import (
    EntityWatcherRepository,
)


class EntityWatcherService:
    def __init__(self, repository: EntityWatcherRepository) -> None:
        super().__init__()
        self.repository = repository

    async def add_watcher(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        user_id: UUID,
    ) -> list[User]:
        if await self.repository.is_watching(entity_type, entity_id, user_id):
            raise ConflictError("User is already watching this entity")

        _ = await self.repository.add_watcher(entity_type, entity_id, user_id)
        return await self.repository.get_watcher_users(entity_type, entity_id)

    async def remove_watcher(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        user_id: UUID,
    ) -> list[User]:
        removed = await self.repository.remove_watcher(entity_type, entity_id, user_id)
        if not removed:
            raise NotFoundError("Watcher")
        return await self.repository.get_watcher_users(entity_type, entity_id)

    async def get_watchers(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[User]:
        return await self.repository.get_watcher_users(entity_type, entity_id)
