from uuid import UUID

from commons.db.v6.core.aliases.alias_entity_type import AliasEntityType
from commons.db.v6.core.aliases.alias_model import Alias
from commons.db.v6.core.aliases.alias_sub_type import AliasSubType

from app.errors.common_errors import NotFoundError
from app.graphql.aliases.repositories.alias_repository import AliasRepository
from app.graphql.aliases.strawberry.alias_input import AliasInput


class AliasService:
    def __init__(self, repository: AliasRepository) -> None:
        super().__init__()
        self.repository = repository

    async def get_by_id(self, alias_id: UUID) -> Alias:
        alias = await self.repository.get_by_id(alias_id)
        if not alias:
            raise NotFoundError(f"Alias with id {alias_id} not found")
        return alias

    async def get_by_entity(
        self,
        entity_id: UUID,
        entity_type: AliasEntityType,
        sub_type: AliasSubType | None = None,
    ) -> list[Alias]:
        return await self.repository.get_by_entity(entity_id, entity_type, sub_type)

    async def search_by_alias(
        self,
        search_term: str,
        entity_type: AliasEntityType | None = None,
        sub_type: AliasSubType | None = None,
        limit: int = 20,
    ) -> list[Alias]:
        return await self.repository.search_by_alias(
            search_term, entity_type, sub_type, limit
        )

    async def create(self, alias_input: AliasInput) -> Alias:
        alias = await self.repository.create(alias_input.to_orm_model())
        return await self.get_by_id(alias.id)

    async def delete(self, alias_id: UUID) -> bool:
        if not await self.repository.exists(alias_id):
            raise NotFoundError(f"Alias with id {alias_id} not found")
        return await self.repository.delete(alias_id)
