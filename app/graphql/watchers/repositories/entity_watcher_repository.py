from uuid import UUID

from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.entity_watcher_model import EntityWatcher
from commons.db.v6.user import User
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


class EntityWatcherRepository:
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    async def add_watcher(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        user_id: UUID,
    ) -> EntityWatcher:
        watcher = EntityWatcher(
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
        )
        self.session.add(watcher)
        await self.session.flush([watcher])
        return watcher

    async def remove_watcher(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        user_id: UUID,
    ) -> bool:
        stmt = delete(EntityWatcher).where(
            EntityWatcher.entity_type == entity_type,
            EntityWatcher.entity_id == entity_id,
            EntityWatcher.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return (getattr(result, "rowcount", 0) or 0) > 0

    async def get_watchers(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[EntityWatcher]:
        stmt = (
            select(EntityWatcher)
            .options(joinedload(EntityWatcher.user))
            .where(
                EntityWatcher.entity_type == entity_type,
                EntityWatcher.entity_id == entity_id,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_watcher_users(
        self,
        entity_type: EntityType,
        entity_id: UUID,
    ) -> list[User]:
        watchers = await self.get_watchers(entity_type, entity_id)
        return [w.user for w in watchers]

    async def is_watching(
        self,
        entity_type: EntityType,
        entity_id: UUID,
        user_id: UUID,
    ) -> bool:
        stmt = select(EntityWatcher).where(
            EntityWatcher.entity_type == entity_type,
            EntityWatcher.entity_id == entity_id,
            EntityWatcher.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
