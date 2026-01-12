from uuid import UUID

from commons.db.v6.warehouse.inventory.inventory import Inventory

from app.core.constants import DEFAULT_QUERY_LIMIT, DEFAULT_QUERY_OFFSET
from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.inventory.repositories.inventory_repository import (
    InventoryRepository,
)
from app.graphql.v2.core.inventory.strawberry.inventory_stats_response import (
    InventoryStatsResponse,
)


class InventoryService:
    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        repository: InventoryRepository,
    ) -> None:
        self.repository = repository

    async def get_by_id(self, inventory_id: UUID) -> Inventory:
        inventory = await self.repository.get_by_id(inventory_id)
        if not inventory:
            raise NotFoundError(f"Inventory with id {inventory_id} not found")
        return inventory

    async def list_by_warehouse(
        self,
        warehouse_id: UUID,
        factory_id: UUID | None = None,
        status: str | None = None,
        search: str | None = None,
        limit: int = DEFAULT_QUERY_LIMIT,
        offset: int = DEFAULT_QUERY_OFFSET,
    ) -> list[Inventory]:
        return await self.repository.find_by_warehouse(
            warehouse_id=warehouse_id,
            factory_id=factory_id,
            status=status,
            search=search,
            limit=limit,
            offset=offset,
        )

    async def get_stats(self, warehouse_id: UUID) -> InventoryStatsResponse:
        return await self.repository.get_stats_by_warehouse(warehouse_id)

    async def create(self, inventory: Inventory) -> Inventory:
        return await self.repository.create(inventory)

    async def update(self, inventory: Inventory) -> Inventory:
        return await self.repository.update(inventory)

    async def delete(self, inventory_id: UUID) -> bool:
        if not await self.repository.exists(inventory_id):
            raise NotFoundError(f"Inventory with id {inventory_id} not found")
        return await self.repository.delete(inventory_id)
