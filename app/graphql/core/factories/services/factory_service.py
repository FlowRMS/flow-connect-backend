from uuid import UUID

from commons.auth import AuthInfo

from app.errors.common_errors import NotFoundError
from app.graphql.core.factories.models import FactoryV2
from app.graphql.core.factories.repositories.factories_repository import (
    FactoriesRepository,
)
from app.graphql.core.factories.strawberry.factory_input import FactoryInput
from app.graphql.links.models.entity_type import EntityType


class FactoryService:
    def __init__(
        self,
        repository: FactoriesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, factory_id: UUID) -> FactoryV2:
        factory = await self.repository.get_by_id(factory_id)
        if not factory:
            raise NotFoundError(f"FactoryV2 with id {factory_id} not found")
        return factory

    async def create(self, factory_input: FactoryInput) -> FactoryV2:
        return await self.repository.create(factory_input.to_orm_model())

    async def update(self, factory_id: UUID, factory_input: FactoryInput) -> FactoryV2:
        factory = factory_input.to_orm_model()
        factory.id = factory_id
        return await self.repository.update(factory)

    async def delete(self, factory_id: UUID) -> bool:
        if not await self.repository.exists(factory_id):
            raise NotFoundError(f"FactoryV2 with id {factory_id} not found")
        return await self.repository.delete(factory_id)

    async def search_factories(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[FactoryV2]:
        return await self.repository.search_by_title(search_term, published, limit)

    async def search_factories_ordered(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[FactoryV2]:
        return await self.repository.search_by_title_ordered(
            search_term, published, limit
        )

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[FactoryV2]:
        return await self.repository.find_by_entity(entity_type, entity_id)

    async def update_manufacturer_order(self, factory_ids: list[UUID]) -> int:
        return await self.repository.update_manufacturer_order(factory_ids)
