from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.territories.services.territory_service import TerritoryService
from app.graphql.v2.core.territories.strawberry.territory_input import TerritoryInput
from app.graphql.v2.core.territories.strawberry.territory_response import (
    TerritoryResponse,
)


@strawberry.type
class TerritoryMutations:
    @strawberry.mutation
    @inject
    async def create_territory(
        self,
        input: TerritoryInput,
        service: Injected[TerritoryService],
    ) -> TerritoryResponse:
        territory = await service.create(input)
        return TerritoryResponse.from_orm_model(territory)

    @strawberry.mutation
    @inject
    async def update_territory(
        self,
        id: UUID,
        input: TerritoryInput,
        service: Injected[TerritoryService],
    ) -> TerritoryResponse:
        territory = await service.update(id, input)
        return TerritoryResponse.from_orm_model(territory)

    @strawberry.mutation
    @inject
    async def delete_territory(
        self,
        id: UUID,
        service: Injected[TerritoryService],
    ) -> bool:
        return await service.delete(id)

    @strawberry.mutation
    @inject
    async def assign_territory_manager(
        self,
        territory_id: UUID,
        user_id: UUID,
        service: Injected[TerritoryService],
    ) -> TerritoryResponse:
        territory = await service.assign_manager(territory_id, user_id)
        return TerritoryResponse.from_orm_model(territory)

    @strawberry.mutation
    @inject
    async def remove_territory_manager(
        self,
        territory_id: UUID,
        user_id: UUID,
        service: Injected[TerritoryService],
    ) -> bool:
        return await service.remove_manager(territory_id, user_id)
