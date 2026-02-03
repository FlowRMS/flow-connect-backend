from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import Warehouse

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class WarehouseLiteResponse(DTOMixin[Warehouse]):
    """Lite response for warehouses - scalar fields only."""

    _instance: strawberry.Private[Warehouse]
    id: UUID
    name: str
    status: str
    latitude: Decimal | None
    longitude: Decimal | None
    description: str | None
    is_active: bool | None
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: Warehouse) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            name=model.name,
            status=model.status,
            latitude=model.latitude,
            longitude=model.longitude,
            description=model.description,
            is_active=model.is_active,
            created_at=model.created_at,
        )
