from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.factories.services.factory_service import FactoryService
from app.graphql.v2.core.factories.strawberry.factory_input import FactoryInput
from app.graphql.v2.core.factories.strawberry.factory_response import FactoryResponse


@strawberry.type
class FactoriesMutations:
    @strawberry.mutation
    @inject
    async def create_factory(
        self,
        input: FactoryInput,
        service: Injected[FactoryService],
    ) -> FactoryResponse:
        factory = await service.create(input)
        return FactoryResponse.from_orm_model(factory)

    @strawberry.mutation
    @inject
    async def update_factory(
        self,
        id: UUID,
        input: FactoryInput,
        service: Injected[FactoryService],
    ) -> FactoryResponse:
        factory = await service.update(id, input)
        return FactoryResponse.from_orm_model(factory)

    @strawberry.mutation
    @inject
    async def delete_factory(
        self,
        id: UUID,
        service: Injected[FactoryService],
    ) -> bool:
        return await service.delete(id)

    @strawberry.mutation
    @inject
    async def update_manufacturer_order(
        self,
        factory_ids: list[UUID],
        service: Injected[FactoryService],
    ) -> int:
        return await service.update_manufacturer_order(factory_ids)
