from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.warehouse.shipment_requests import (
    ShipmentMethod,
    ShipmentPriority,
    ShipmentRequest,
    ShipmentRequestStatus,
)

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.shipment_requests.strawberry.shipment_request_item_response import (
    ShipmentRequestItemResponse,
)


@strawberry.type
class ShipmentRequestResponse(DTOMixin[ShipmentRequest]):
    _instance: strawberry.Private[ShipmentRequest]
    id: UUID
    request_number: str
    warehouse_id: UUID | None
    factory_id: UUID | None
    status: ShipmentRequestStatus
    method: ShipmentMethod | None
    priority: ShipmentPriority
    notes: str | None
    request_date: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_model(cls, model: ShipmentRequest) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            request_number=model.request_number,
            warehouse_id=model.warehouse_id,
            factory_id=model.factory_id,
            status=model.status,
            method=model.method,
            priority=model.priority,
            notes=model.notes,
            request_date=model.request_date,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @strawberry.field
    def items(self) -> list[ShipmentRequestItemResponse]:
        return ShipmentRequestItemResponse.from_orm_model_list(self._instance.items)

    @strawberry.field
    def total_quantity(self) -> Decimal:
        return sum((item.quantity for item in self._instance.items), Decimal("0"))

    @strawberry.field
    def factory(self) -> FactoryLiteResponse | None:
        factory = self._instance.factory
        if not factory:
            return None
        return FactoryLiteResponse.from_orm_model(factory)
