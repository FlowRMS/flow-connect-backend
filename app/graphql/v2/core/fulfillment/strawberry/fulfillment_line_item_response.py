from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentOrderLineItem

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.fulfillment.strawberry.packing_box_response import (
    PackingBoxItemResponse,
)


@strawberry.type
class FulfillmentOrderLineItemResponse(DTOMixin[FulfillmentOrderLineItem]):
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
    async def product_name(self) -> str:
        product = await self._instance.awaitable_attrs.product
        return product.factory_part_number if product else ""

    @strawberry.field
    async def part_number(self) -> str:
        """Get the product's factory part number."""
        product = await self._instance.awaitable_attrs.product
        return product.factory_part_number if product else ""

    @strawberry.field
    async def uom(self) -> str:
        """Get the product's unit of measure."""
        product = await self._instance.awaitable_attrs.product
        if product:
            uom_obj = await product.awaitable_attrs.uom
            return uom_obj.title if uom_obj else "EA"
        return "EA"

    @strawberry.field
    async def packing_box_items(self) -> list[PackingBoxItemResponse]:
        items = await self._instance.awaitable_attrs.packing_box_items
        return PackingBoxItemResponse.from_orm_model_list(items)

    @strawberry.field
    async def factory_id(self) -> UUID | None:
        """Get the product's factory/manufacturer ID."""
        product = await self._instance.awaitable_attrs.product
        return product.factory_id if product else None

    @strawberry.field
    async def factory_name(self) -> str | None:
        """Get the product's factory/manufacturer name."""
        product = await self._instance.awaitable_attrs.product
        if product and product.factory_id:
            factory = await product.awaitable_attrs.factory
            return factory.title if factory else None
        return None
