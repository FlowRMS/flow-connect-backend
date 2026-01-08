from uuid import UUID

from decimal import Decimal
import strawberry
from commons.db.v6.warehouse.inventory.inventory_item import (
    InventoryItem,
    InventoryItemStatus,
)

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.inventory.repositories.inventory_item_repository import (
    InventoryItemRepository,
)
from app.graphql.v2.core.inventory.repositories.inventory_repository import (
    InventoryRepository,
)


from app.core.constants import DEFAULT_QUERY_LIMIT, DEFAULT_QUERY_OFFSET

class InventoryItemService:
    def __init__(
        self,
        item_repository: InventoryItemRepository,
        inventory_repository: InventoryRepository,
    ) -> None:
        self.item_repository = item_repository
        self.inventory_repository = inventory_repository

    async def get_by_id(self, item_id: UUID) -> InventoryItem:
        item = await self.item_repository.get_by_id(item_id)
        if not item:
            raise NotFoundError(f"InventoryItem with id {item_id} not found")
        return item

    async def add_item(self, item: InventoryItem) -> InventoryItem:
        inventory = await self.inventory_repository.get_by_id(item.inventory_id)
        if not inventory:
            raise NotFoundError(f"Inventory with id {item.inventory_id} not found")

        created_item = await self.item_repository.create(item)

        inventory.total_quantity += item.quantity
        if item.status == InventoryItemStatus.AVAILABLE:
            inventory.available_quantity += item.quantity
        _ = await self.inventory_repository.update(inventory)

        return created_item

    async def list_by_inventory(
        self,
        inventory_id: UUID,
        limit: int = DEFAULT_QUERY_LIMIT,
        offset: int = DEFAULT_QUERY_OFFSET,
    ) -> list[InventoryItem]:
        return await self.item_repository.find_by_inventory_id(
            inventory_id=inventory_id,
            limit=limit,
            offset=offset,
        )

    async def delete(self, item_id: UUID) -> bool:
        item = await self.get_by_id(item_id)

        inventory = await self.inventory_repository.get_by_id(item.inventory_id)
        if inventory:
            inventory.total_quantity -= item.quantity
            if item.status == InventoryItemStatus.AVAILABLE:
                inventory.available_quantity -= item.quantity
            _ = await self.inventory_repository.update(inventory)

        return await self.item_repository.delete(item_id)

    async def update_item(
        self,
        item_id: UUID,
        location_id: UUID | None | object = strawberry.UNSET,
        quantity: Decimal | None | object = strawberry.UNSET,
        status: InventoryItemStatus | None | object = strawberry.UNSET,
    ) -> InventoryItem:
        item = await self.get_by_id(item_id)

        # 1. Capture old state
        old_quantity = item.quantity
        old_status = item.status

        # 2. Apply changes
        if quantity is not strawberry.UNSET and isinstance(quantity, Decimal):
            item.quantity = quantity

        if location_id is not strawberry.UNSET:
             item.location_id = location_id if location_id is not None else None

        if status is not strawberry.UNSET and isinstance(status, InventoryItemStatus):
            item.status = status

        # 3. Calculate Diffs
        total_diff = item.quantity - old_quantity
        
        old_available = old_quantity if old_status == InventoryItemStatus.AVAILABLE else Decimal(0)
        new_available = item.quantity if item.status == InventoryItemStatus.AVAILABLE else Decimal(0)
        available_diff = new_available - old_available

        # 4. Update Inventory stats if needed
        if total_diff != Decimal(0) or available_diff != Decimal(0):
            inventory = await self.inventory_repository.get_by_id(item.inventory_id)
            if inventory:
                inventory.total_quantity += total_diff
                inventory.available_quantity += available_diff
                _ = await self.inventory_repository.update(inventory)

        return await self.item_repository.update(item)
