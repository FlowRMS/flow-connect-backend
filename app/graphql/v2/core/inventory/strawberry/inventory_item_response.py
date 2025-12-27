from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from commons.db.v6.crm.inventory.inventory_item import InventoryItem


@strawberry.enum
class InventoryItemStatusEnum(strawberry.enum.Enum):
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    PICKING = "PICKING"
    DAMAGED = "DAMAGED"
    QUARANTINE = "QUARANTINE"


@strawberry.type
class InventoryItemResponse(DTOMixin[InventoryItem]):
    id: UUID
    inventory_id: UUID
    bin_id: UUID | None
    bin_location: str | None
    full_location_path: str | None
    quantity: int
    lot_number: str | None
    status: InventoryItemStatusEnum
    received_date: datetime | None

    @classmethod
    def from_orm_model(cls, model: InventoryItem) -> Self:
        return cls(
            id=model.id,
            inventory_id=model.inventory_id,
            bin_id=model.bin_id,
            bin_location=model.bin_location,
            full_location_path=model.full_location_path,
            quantity=model.quantity,
            lot_number=model.lot_number,
            status=InventoryItemStatusEnum(model.status.value),
            received_date=model.received_date,
        )
