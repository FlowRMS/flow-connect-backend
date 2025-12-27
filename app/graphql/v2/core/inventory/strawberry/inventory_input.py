from datetime import datetime
from uuid import UUID

import strawberry

from commons.db.v6.crm.inventory.inventory_item import (
    InventoryItem,
    InventoryItemStatus,
)
from app.graphql.v2.core.inventory.strawberry.inventory_item_response import (
    InventoryItemStatusEnum,
)


@strawberry.input
class AddInventoryItemInput:
    inventory_id: UUID
    bin_id: UUID | None = None
    bin_location: str | None = None
    full_location_path: str | None = None
    quantity: int = 0
    lot_number: str | None = None
    status: InventoryItemStatusEnum = InventoryItemStatusEnum.AVAILABLE
    received_date: datetime | None = None

    def to_orm_model(self) -> InventoryItem:
        return InventoryItem(
            inventory_id=self.inventory_id,
            bin_id=self.bin_id,
            bin_location=self.bin_location,
            full_location_path=self.full_location_path,
            quantity=self.quantity,
            lot_number=self.lot_number,
            status=InventoryItemStatus(self.status.value),
            received_date=self.received_date,
        )


@strawberry.input
class CreateInventoryInput:
    product_id: str
    product_name: str
    part_number: str
    warehouse_id: UUID
    factory_id: UUID | None = None
    factory_name: str | None = None
    total_quantity: int = 0
    available_quantity: int = 0
    reserved_quantity: int = 0
    picking_quantity: int = 0
    reorder_point: int | None = None
