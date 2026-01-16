from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.warehouse.inventory.inventory_item import InventoryItemStatus

from app.graphql.inject import inject
from app.graphql.v2.core.inventory.services.inventory_service import InventoryService
from app.graphql.v2.core.inventory.strawberry.inventory_response import (
    InventoryResponse,
)
from app.graphql.v2.core.inventory.strawberry.inventory_stats_response import (
    InventoryStatsResponse,
)


@strawberry.type
class InventoryStatusOption:
    label: str
    value: str


from app.core.constants import DEFAULT_QUERY_LIMIT, DEFAULT_QUERY_OFFSET


@strawberry.type
class InventoryQueries:
    @strawberry.field
    def inventory_statuses(self) -> list[InventoryStatusOption]:
        return [
            InventoryStatusOption(
                label=status.name.replace("_", " ").title(), value=status.name
            )
            for status in InventoryItemStatus
        ]

    @strawberry.field
    @inject
    async def inventories(
        self,
        service: Injected[InventoryService],
        warehouse_id: UUID,
        factory_id: UUID | None = None,
        status: str | None = None,
        search: str | None = None,
        limit: int = DEFAULT_QUERY_LIMIT,
        offset: int = DEFAULT_QUERY_OFFSET,
    ) -> list[InventoryResponse]:
        inventories = await service.list_by_warehouse(
            warehouse_id=warehouse_id,
            factory_id=factory_id,
            status=status,
            search=search,
            limit=limit,
            offset=offset,
        )
        return InventoryResponse.from_orm_model_list(inventories)

    @strawberry.field
    @inject
    async def inventory_stats(
        self,
        service: Injected[InventoryService],
        warehouse_id: UUID,
    ) -> InventoryStatsResponse:
        return await service.get_stats(warehouse_id)

    @strawberry.field
    @inject
    async def inventory_by_id(
        self,
        service: Injected[InventoryService],
        id: UUID,
    ) -> InventoryResponse:
        inventory = await service.get_by_id(id)
        return InventoryResponse.from_orm_model(inventory)
