from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.inventory import InventoryItem, InventoryItemStatus

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class InventoryItemResponse(DTOMixin[InventoryItem]):
    id: UUID
    inventory_id: UUID
    bin_id: UUID | None
    bin_location: str | None
    full_location_path: str | None
    quantity: Decimal
    lot_number: str | None
    status: InventoryItemStatus
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
            status=model.status,
            received_date=model.received_date,
        )
