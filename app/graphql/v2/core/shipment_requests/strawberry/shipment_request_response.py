from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry

from app.core.db.adapters.dto import DTOMixin
from commons.db.v6.crm.shipment_requests.shipment_request import (
    ShipmentRequest,
)
from app.graphql.v2.core.shipment_requests.strawberry.shipment_request_item_response import (
    ShipmentRequestItemResponse,
)


@strawberry.enum
class ShipmentRequestStatusEnum(strawberry.enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    IN_PROGRESS = "IN_PROGRESS"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


@strawberry.type
class ShipmentRequestResponse(DTOMixin[ShipmentRequest]):
    _instance: strawberry.Private[ShipmentRequest]
    id: UUID
    warehouse_id: UUID
    factory_id: UUID | None
    status: ShipmentRequestStatusEnum
    notes: str | None
    requested_delivery_date: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_model(cls, model: ShipmentRequest) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            warehouse_id=model.warehouse_id,
            factory_id=model.factory_id,
            status=ShipmentRequestStatusEnum(model.status.value),
            notes=model.notes,
            requested_delivery_date=model.requested_delivery_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @strawberry.field
    async def items(self) -> list[ShipmentRequestItemResponse]:
        items = await self._instance.awaitable_attrs.items
        return ShipmentRequestItemResponse.from_orm_model_list(items)
