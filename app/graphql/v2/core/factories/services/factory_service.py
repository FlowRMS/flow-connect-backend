from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.core.factories.factory import Factory
from commons.db.v6.core.factories.factory_split_rate import FactorySplitRate
from commons.db.v6.crm.links.entity_type import EntityType
from sqlalchemy.orm import joinedload, lazyload

from app.errors.common_errors import NameAlreadyExistsError, NotFoundError
from app.graphql.v2.core.factories.repositories.factories_repository import (
    FactoriesRepository,
)
from app.graphql.v2.core.factories.strawberry.factory_input import FactoryInput


class FactoryService:
    def __init__(
        self,
        repository: FactoriesRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, factory_id: UUID) -> Factory:
        factory = await self.repository.get_by_id(
            factory_id,
            options=[
                joinedload(Factory.split_rates),
                joinedload(Factory.split_rates).joinedload(FactorySplitRate.user),
                joinedload(Factory.created_by),
                joinedload(Factory.parent),
                lazyload("*"),
            ],
        )
        if not factory:
            raise NotFoundError(f"Factory with id {factory_id} not found")
        return factory

    async def create(self, factory_input: FactoryInput) -> Factory:
        if await self.repository.title_exists(factory_input.title):
            raise NameAlreadyExistsError(factory_input.title)

        factory = await self.repository.create(factory_input.to_orm_model())
        return await self.get_by_id(factory.id)

    async def update(self, factory_id: UUID, factory_input: FactoryInput) -> Factory:
        factory = factory_input.to_orm_model()
        factory.id = factory_id
        _ = await self.repository.update(factory)
        return await self.get_by_id(factory_id)

    async def delete(self, factory_id: UUID) -> bool:
        if not await self.repository.exists(factory_id):
            raise NotFoundError(f"Factory with id {factory_id} not found")
        return await self.repository.delete(factory_id)

    async def search_factories(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[Factory]:
        return await self.repository.search_by_title(search_term, published, limit)

    async def search_factories_ordered(
        self, search_term: str, published: bool = True, limit: int = 20
    ) -> list[Factory]:
        return await self.repository.search_by_title_ordered(
            search_term, published, limit
        )

    async def find_by_entity(
        self, entity_type: EntityType, entity_id: UUID
    ) -> list[Factory]:
        return await self.repository.find_by_entity(entity_type, entity_id)

    async def update_manufacturer_order(self, factory_ids: list[UUID]) -> int:
        return await self.repository.update_manufacturer_order(factory_ids)

    async def get_children(self, parent_id: UUID) -> list[Factory]:
        return await self.repository.get_children(parent_id)

    async def assign_children(
        self,
        parent_id: UUID,
        child_ids: list[UUID],
    ) -> list[Factory]:
        if not await self.repository.exists(parent_id):
            raise NotFoundError(f"Parent factory with id {parent_id} not found")

        await self.repository.set_children_parent_id(parent_id, child_ids)
        return await self.repository.get_children(parent_id)
