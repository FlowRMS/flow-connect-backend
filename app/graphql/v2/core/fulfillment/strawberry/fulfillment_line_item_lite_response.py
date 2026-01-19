"""Lite response type for fulfillment order line items."""

from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentOrderLineItem

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class FulfillmentOrderLineItemLiteResponse(DTOMixin[FulfillmentOrderLineItem]):
    """Lite response for line items - scalar fields + synchronous accessors."""

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
    def product_name(self) -> str:
        """Get product name - product is eager-loaded."""
        return self._instance.product.factory_part_number if self._instance.product else ""

    @strawberry.field
    def part_number(self) -> str:
        """Get product part number - product is eager-loaded."""
        return self._instance.product.factory_part_number if self._instance.product else ""

    @strawberry.field
    def uom(self) -> str:
        """Get UOM title - product.uom is eager-loaded."""
        if self._instance.product and self._instance.product.uom:
            return self._instance.product.uom.title
        return "EA"

    @strawberry.field
    def factory_id(self) -> UUID | None:
        """Get factory ID - product is eager-loaded."""
        return self._instance.product.factory_id if self._instance.product else None

    @strawberry.field
    def factory_name(self) -> str | None:
        """Get factory name - product.factory is eager-loaded."""
        if self._instance.product and self._instance.product.factory:
            return self._instance.product.factory.title
        return None
