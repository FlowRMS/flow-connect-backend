from uuid import UUID

from decimal import Decimal
import strawberry
from commons.db.v6.warehouse.inventory.inventory_item import InventoryItem

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.inventory.repositories.inventory_item_repository import (
    InventoryItemRepository,
)
from app.graphql.v2.core.inventory.repositories.inventory_repository import (
    InventoryRepository,
)


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
        inventory.available_quantity += item.quantity
        await self.inventory_repository.update(inventory)

        return created_item

    async def list_by_inventory(
        self,
        inventory_id: UUID,
        limit: int = 100,
        offset: int = 0,
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
            inventory.available_quantity -= item.quantity
            await self.inventory_repository.update(inventory)

        return await self.item_repository.delete(item_id)

    async def update_item(
        self,
        item_id: UUID,
        location_id: UUID | None | object = strawberry.UNSET,
        quantity: Decimal | None | object = strawberry.UNSET,
        status: object | None = strawberry.UNSET,  # Type hint object for UNSET
    ) -> InventoryItem:
        item = await self.get_by_id(item_id)
        
        # Calculate quantity diff if changing
        quantity_diff = Decimal(0)
        if quantity is not strawberry.UNSET and quantity is not None:
             # Check type at runtime to be safe if strawberry allows it
             qty_decimal = Decimal(quantity) # type: ignore
             quantity_diff = qty_decimal - item.quantity
             item.quantity = qty_decimal

        if location_id is not strawberry.UNSET:
            item.location_id = location_id # type: ignore

        if status is not strawberry.UNSET:
             item.status = status # type: ignore

        # Update Inventory stats if quantity changed
        if quantity_diff != 0:
            inventory = await self.inventory_repository.get_by_id(item.inventory_id)
            if inventory:
                inventory.total_quantity += quantity_diff
                inventory.available_quantity += quantity_diff
                await self.inventory_repository.update(inventory)

        return await self.item_repository.update(item)
