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
from app.graphql.orders.strawberry.order_lite_response import OrderLiteResponse
from app.graphql.v2.core.customers.strawberry.customer_response import CustomerLiteResponse
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_assignment_response import (
    FulfillmentAssignmentResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_line_item_lite_response import (
    FulfillmentOrderLineItemLiteResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.shipping_carrier_lite_response import (
    ShippingCarrierLiteResponse,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_lite_response import (
    WarehouseLiteResponse,
)


@strawberry.type
class FulfillmentOrderLiteResponse(DTOMixin[FulfillmentOrder]):
    """Lite response for list endpoints - scalar fields + nested Lite responses."""

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
    service_type: str | None
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
            service_type=model.service_type,
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
    def warehouse(self) -> WarehouseLiteResponse | None:
        """Get warehouse - relationship is eager-loaded."""
        if self._instance.warehouse:
            return WarehouseLiteResponse.from_orm_model(self._instance.warehouse)
        return None

    @strawberry.field
    def carrier(self) -> ShippingCarrierLiteResponse | None:
        """Get carrier - relationship is eager-loaded."""
        if self._instance.carrier:
            return ShippingCarrierLiteResponse.from_orm_model(self._instance.carrier)
        return None

    @strawberry.field
    def order(self) -> OrderLiteResponse | None:
        """Get the sales order - relationship is eager-loaded."""
        if self._instance.order:
            return OrderLiteResponse.from_orm_model(self._instance.order)
        return None

    @strawberry.field
    def customer(self) -> CustomerLiteResponse | None:
        """Get the sold-to customer via the order relationship - eager-loaded."""
        if self._instance.order and self._instance.order.sold_to_customer:
            return CustomerLiteResponse.from_orm_model(self._instance.order.sold_to_customer)
        return None

    @strawberry.field
    def line_items(self) -> list[FulfillmentOrderLineItemLiteResponse]:
        """Get line items - relationship is eager-loaded."""
        return [
            FulfillmentOrderLineItemLiteResponse.from_orm_model(li)
            for li in (self._instance.line_items or [])
        ]

    @strawberry.field
    def assignments(self) -> list[FulfillmentAssignmentResponse]:
        """Get assignments - relationship is eager-loaded."""
        return [
            FulfillmentAssignmentResponse.from_orm_model(a)
            for a in (self._instance.assignments or [])
        ]
