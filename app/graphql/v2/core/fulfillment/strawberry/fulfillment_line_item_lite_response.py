"""Lite response type for fulfillment order line items."""

from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentOrderLineItem

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_product_response import (
    FulfillmentProductResponse,
)


@strawberry.type
class FulfillmentOrderLineItemLiteResponse(DTOMixin[FulfillmentOrderLineItem]):
    """Lite response for line items - scalar fields + nested Lite responses."""

    _instance: strawberry.Private[FulfillmentOrderLineItem]
    id: UUID
    product_id: UUID
    order_detail_id: UUID | None
    ordered_qty: Decimal
    allocated_qty: Decimal
    picked_qty: Decimal
    packed_qty: Decimal
    shipped_qty: Decimal
    backorder_qty: Decimal
    fulfilled_by_manufacturer: bool
    manufacturer_fulfillment_status: str | None
    linked_shipment_request_id: UUID | None
    short_reason: str | None
    notes: str | None

    @classmethod
    def from_orm_model(cls, model: FulfillmentOrderLineItem) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            product_id=model.product_id,
            order_detail_id=model.order_detail_id,
            ordered_qty=model.ordered_qty,
            allocated_qty=model.allocated_qty,
            picked_qty=model.picked_qty,
            packed_qty=model.packed_qty,
            shipped_qty=model.shipped_qty,
            backorder_qty=model.backorder_qty,
            fulfilled_by_manufacturer=model.fulfilled_by_manufacturer,
            manufacturer_fulfillment_status=model.manufacturer_fulfillment_status,
            linked_shipment_request_id=model.linked_shipment_request_id,
            short_reason=model.short_reason,
            notes=model.notes,
        )

    @strawberry.field
    def product(self) -> FulfillmentProductResponse | None:
        """Get product - relationship is eager-loaded."""
        if self._instance.product:
            return FulfillmentProductResponse.from_orm_model(self._instance.product)
        return None
