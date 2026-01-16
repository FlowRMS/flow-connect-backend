from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.core.territories.territory_type_enum import (
    TerritoryTypeEnum,
)

from app.graphql.inject import inject
from app.graphql.v2.core.territories.services.territory_service import TerritoryService
from app.graphql.v2.core.territories.strawberry.territory_response import (
    TerritoryLiteResponse,
    TerritoryResponse,
)


@strawberry.type
class TerritoryQueries:
    @strawberry.field
    @inject
    async def territory(
        self,
        id: UUID,
        service: Injected[TerritoryService],
    ) -> TerritoryResponse | None:
        territory = await service.get_by_id_optional(id)
        return TerritoryResponse.from_orm_model_optional(territory)

    @strawberry.field
    @inject
    async def territories_by_type(
        self,
        territory_type: TerritoryTypeEnum,
        service: Injected[TerritoryService],
        active_only: bool = True,
    ) -> list[TerritoryLiteResponse]:
        territories = await service.get_by_type(territory_type, active_only)
        return TerritoryLiteResponse.from_orm_model_list(territories)

    @strawberry.field
    @inject
    async def territory_children(
        self,
        parent_id: UUID,
        service: Injected[TerritoryService],
    ) -> list[TerritoryLiteResponse]:
        children = await service.get_children(parent_id)
        return TerritoryLiteResponse.from_orm_model_list(children)

    @strawberry.field
    @inject
    async def territory_hierarchy(
        self,
        territory_id: UUID,
        service: Injected[TerritoryService],
    ) -> list[TerritoryLiteResponse]:
        hierarchy = await service.get_hierarchy(territory_id)
        return TerritoryLiteResponse.from_orm_model_list(hierarchy)

    @strawberry.field
    @inject
    async def all_territories(
        self,
        service: Injected[TerritoryService],
    ) -> list[TerritoryLiteResponse]:
        territories = await service.get_all_active()
        return TerritoryLiteResponse.from_orm_model_list(territories)
