"""Lite response type for shipping carriers."""

from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.shipping_carriers.shipping_carrier_model import ShippingCarrier
from commons.db.v6.fulfillment.enums import CarrierType

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class ShippingCarrierLiteResponse(DTOMixin[ShippingCarrier]):
    """Lite response for shipping carriers - scalar fields only."""

    _instance: strawberry.Private[ShippingCarrier]
    id: UUID
    name: str
    carrier_type: CarrierType | None
    code: str | None
    is_active: bool | None
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: ShippingCarrier) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            name=model.name,
            carrier_type=model.carrier_type,
            code=model.code,
            is_active=model.is_active,
            created_at=model.created_at,
        )
