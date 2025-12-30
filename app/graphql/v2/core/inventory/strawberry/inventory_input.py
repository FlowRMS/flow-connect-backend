from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.warehouse.inventory import InventoryItem, InventoryItemStatus


@strawberry.input
class AddInventoryItemInput:
    inventory_id: UUID
    location_id: UUID | None = None
    quantity: Decimal = Decimal(0)
    lot_number: str | None = None
    status: InventoryItemStatus = InventoryItemStatus.AVAILABLE
    received_date: datetime | None = None

    def to_orm_model(self) -> InventoryItem:
        return InventoryItem(
            inventory_id=self.inventory_id,
            location_id=self.location_id,
            quantity=self.quantity,
            lot_number=self.lot_number,
            status=self.status,
            received_date=self.received_date,
        )
