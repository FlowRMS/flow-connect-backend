from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.warehouse.inventory import InventoryItem, InventoryItemStatus

from aioinject import Injected
from app.graphql.inject import inject
from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.warehouses.services.warehouse_location_service import (
    WarehouseLocationService,
)


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
    created_at: datetime

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
            created_at=model.created_at,
        )

    @strawberry.field
    @inject
    async def location_name(
        self, service: Injected[WarehouseLocationService]
    ) -> str | None:
        if self._instance.location:
             return self._instance.location.name
        
        if self.location_id:
            try:
                location = await service.get_by_id(self.location_id)
                return location.name
            except Exception:
                pass
        return None
