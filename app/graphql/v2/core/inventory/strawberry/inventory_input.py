from datetime import datetime
from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.crm.inventory import InventoryItem, InventoryItemStatus


@strawberry.input
class AddInventoryItemInput:
    inventory_id: UUID
    bin_id: UUID | None = None
    bin_location: str | None = None
    full_location_path: str | None = None
    quantity: Decimal = Decimal(0)
    lot_number: str | None = None
    status: InventoryItemStatus = InventoryItemStatus.AVAILABLE
    received_date: datetime | None = None

    def to_orm_model(self) -> InventoryItem:
        return InventoryItem(
            inventory_id=self.inventory_id,
            bin_id=self.bin_id,
            bin_location=self.bin_location,
            full_location_path=self.full_location_path,
            quantity=self.quantity,
            lot_number=self.lot_number,
            status=self.status,
            received_date=self.received_date,
        )
