from uuid import UUID

from commons.db.v6.core.aliases.alias_entity_type import AliasEntityType
from commons.db.v6.core.aliases.alias_model import Alias
from commons.db.v6.core.aliases.alias_sub_type import AliasSubType
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class AliasRepository(BaseRepository[Alias]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, Alias)

    async def get_by_entity(
        self,
        entity_id: UUID,
        entity_type: AliasEntityType,
        sub_type: AliasSubType | None = None,
    ) -> list[Alias]:
        stmt = select(Alias).where(
            Alias.entity_id == entity_id,
            Alias.entity_type == entity_type,
        )
        if sub_type is not None:
            stmt = stmt.where(Alias.sub_type == sub_type)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_alias(
        self,
        search_term: str,
        entity_type: AliasEntityType | None = None,
        sub_type: AliasSubType | None = None,
        limit: int = 20,
    ) -> list[Alias]:
        stmt = select(Alias).where(Alias.alias.ilike(f"%{search_term}%"))
        if entity_type is not None:
            stmt = stmt.where(Alias.entity_type == entity_type)
        if sub_type is not None:
            stmt = stmt.where(Alias.sub_type == sub_type)
        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_exact_alias(
        self,
        alias: str,
        entity_type: AliasEntityType,
        entity_id: UUID,
        sub_type: AliasSubType | None = None,
    ) -> Alias | None:
        stmt = select(Alias).where(
            Alias.alias == alias,
            Alias.entity_type == entity_type,
            Alias.entity_id == entity_id,
        )
        if sub_type is not None:
            stmt = stmt.where(Alias.sub_type == sub_type)
        result = await self.session.execute(stmt)
        return result.scalars().first()
