"""Lite response type for fulfillment orders - used for list endpoints."""

from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentOrder
from commons.db.v6.fulfillment.enums import (
    CarrierType,
    FulfillmentMethod,
    FulfillmentOrderStatus,
)

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class FulfillmentOrderLiteResponse(DTOMixin[FulfillmentOrder]):
    """Lite response for list endpoints - scalar fields + synchronous accessors."""

    _instance: strawberry.Private[FulfillmentOrder]
    id: UUID
    fulfillment_order_number: str
    order_id: UUID
    warehouse_id: UUID
    carrier_id: UUID | None
    status: FulfillmentOrderStatus
    fulfillment_method: FulfillmentMethod
    carrier_type: CarrierType | None
    freight_class: str | None
    need_by_date: date | None
    has_backorder_items: bool
    hold_reason: str | None

    # Timestamps
    released_at: datetime | None
    pick_started_at: datetime | None
    pick_completed_at: datetime | None
    pack_completed_at: datetime | None
    ship_confirmed_at: datetime | None
    delivered_at: datetime | None
    created_at: datetime

    # Shipping
    tracking_numbers: list[str]
    bol_number: str | None
    pro_number: str | None

    @classmethod
    def from_orm_model(cls, model: FulfillmentOrder) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            fulfillment_order_number=model.fulfillment_order_number,
            order_id=model.order_id,
            warehouse_id=model.warehouse_id,
            carrier_id=model.carrier_id,
            status=model.status,
            fulfillment_method=model.fulfillment_method,
            carrier_type=model.carrier_type,
            freight_class=model.freight_class,
            need_by_date=model.need_by_date,
            has_backorder_items=model.has_backorder_items,
            hold_reason=model.hold_reason,
            released_at=model.released_at,
            pick_started_at=model.pick_started_at,
            pick_completed_at=model.pick_completed_at,
            pack_completed_at=model.pack_completed_at,
            ship_confirmed_at=model.ship_confirmed_at,
            delivered_at=model.delivered_at,
            created_at=model.created_at,
            tracking_numbers=model.tracking_numbers or [],
            bol_number=model.bol_number,
            pro_number=model.pro_number,
        )

    @strawberry.field
    def warehouse_name(self) -> str:
        """Get warehouse name - relationship is eager-loaded."""
        return self._instance.warehouse.name if self._instance.warehouse else ""

    @strawberry.field
    def carrier_name(self) -> str | None:
        """Get carrier name - relationship is eager-loaded."""
        return self._instance.carrier.name if self._instance.carrier else None

    @strawberry.field
    def order_number(self) -> str:
        """Get the sales order number - relationship is eager-loaded."""
        return self._instance.order.order_number if self._instance.order else ""

    @strawberry.field
    def customer_name(self) -> str:
        """Get customer name - order.sold_to_customer is eager-loaded."""
        if self._instance.order and self._instance.order.sold_to_customer:
            return self._instance.order.sold_to_customer.company_name
        return ""
