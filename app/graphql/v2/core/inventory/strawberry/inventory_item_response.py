from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.warehouse.inventory import InventoryItem, InventoryItemStatus

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class InventoryItemResponse(DTOMixin[InventoryItem]):
    _instance: strawberry.Private[InventoryItem]
    id: UUID
    inventory_id: UUID
    location_id: UUID | None
    quantity: Decimal
    lot_number: str | None
    status: InventoryItemStatus
    received_date: datetime | None

    @classmethod
    def from_orm_model(cls, model: InventoryItem) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            inventory_id=model.inventory_id,
            location_id=model.location_id,
            quantity=model.quantity,
            lot_number=model.lot_number,
            status=model.status,
            received_date=model.received_date,
        )

    @strawberry.field
    async def location_name(self) -> str | None:
        location = await self._instance.awaitable_attrs.location
        if location:
            return location.name
        return None
