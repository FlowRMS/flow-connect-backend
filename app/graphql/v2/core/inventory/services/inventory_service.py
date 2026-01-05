from uuid import UUID

from commons.db.v6.warehouse.inventory.inventory import Inventory

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.inventory.repositories.inventory_repository import (
    InventoryRepository,
)
from app.graphql.v2.core.inventory.strawberry.inventory_stats_response import (
    InventoryStatsResponse,
)


class InventoryService:
    def __init__(
        self,
        repository: InventoryRepository,
    ) -> None:
        super().__init__()
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
        limit: int = 100,
        offset: int = 0,
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

    async def get_by_product(
        self,
        product_id: UUID,
        warehouse_id: UUID | None = None,
    ) -> Inventory | None:
        """Get inventory for a specific product, optionally in a specific warehouse."""
        return await self.repository.find_by_product(product_id, warehouse_id)

    async def get_by_products(
        self,
        product_ids: list[UUID],
        warehouse_id: UUID,
    ) -> list[Inventory]:
        """Get inventory for multiple products in a warehouse."""
        return await self.repository.find_by_products(product_ids, warehouse_id)

    async def create(self, inventory: Inventory) -> Inventory:
        return await self.repository.create(inventory)

    async def update(self, inventory: Inventory) -> Inventory:
        return await self.repository.update(inventory)

    async def delete(self, inventory_id: UUID) -> bool:
        if not await self.repository.exists(inventory_id):
            raise NotFoundError(f"Inventory with id {inventory_id} not found")
        return await self.repository.delete(inventory_id)
