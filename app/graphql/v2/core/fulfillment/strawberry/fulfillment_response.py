from datetime import date, datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import (
    CarrierType,
    FulfillmentActivity,
    FulfillmentActivityType,
    FulfillmentAssignment,
    FulfillmentAssignmentRole,
    FulfillmentMethod,
    FulfillmentOrder,
    FulfillmentOrderLineItem,
    FulfillmentOrderStatus,
    PackingBox,
    PackingBoxItem,
)

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class ShipToAddressResponse:
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None


@strawberry.type
class FulfillmentActivityResponse(DTOMixin[FulfillmentActivity]):
    _instance: strawberry.Private[FulfillmentActivity]
    id: UUID
    activity_type: FulfillmentActivityType
    content: str | None
    metadata: strawberry.scalars.JSON | None
    created_at: datetime
    created_by_id: UUID

    @classmethod
    def from_orm_model(cls, model: FulfillmentActivity) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            activity_type=model.activity_type,
            content=model.content,
            metadata=model.metadata,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
        )


@strawberry.type
class FulfillmentAssignmentResponse(DTOMixin[FulfillmentAssignment]):
    _instance: strawberry.Private[FulfillmentAssignment]
    id: UUID
    user_id: UUID
    role: FulfillmentAssignmentRole
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: FulfillmentAssignment) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            user_id=model.user_id,
            role=model.role,
            created_at=model.created_at,
        )

    @strawberry.field
    async def user_name(self) -> str:
        user = await self._instance.awaitable_attrs.user
        return user.full_name if user else ""

    @strawberry.field
    async def user_email(self) -> str:
        user = await self._instance.awaitable_attrs.user
        return user.email if user else ""


@strawberry.type
class PackingBoxItemResponse(DTOMixin[PackingBoxItem]):
    _instance: strawberry.Private[PackingBoxItem]
    id: UUID
    fulfillment_line_item_id: UUID
    quantity: Decimal

    @classmethod
    def from_orm_model(cls, model: PackingBoxItem) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            fulfillment_line_item_id=model.fulfillment_line_item_id,
            quantity=model.quantity,
        )


@strawberry.type
class PackingBoxResponse(DTOMixin[PackingBox]):
    _instance: strawberry.Private[PackingBox]
    id: UUID
    box_number: int
    container_type_id: UUID | None
    length: Decimal | None
    width: Decimal | None
    height: Decimal | None
    weight: Decimal | None
    tracking_number: str | None
    label_printed_at: datetime | None
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: PackingBox) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            box_number=model.box_number,
            container_type_id=model.container_type_id,
            length=model.length,
            width=model.width,
            height=model.height,
            weight=model.weight,
            tracking_number=model.tracking_number,
            label_printed_at=model.label_printed_at,
            created_at=model.created_at,
        )

    @strawberry.field
    async def container_type_name(self) -> str | None:
        container_type = await self._instance.awaitable_attrs.container_type
        return container_type.name if container_type else None

    @strawberry.field
    async def items(self) -> list[PackingBoxItemResponse]:
        items = await self._instance.awaitable_attrs.items
        return PackingBoxItemResponse.from_orm_model_list(items)


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


@strawberry.type
class FulfillmentOrderResponse(DTOMixin[FulfillmentOrder]):
    _instance: strawberry.Private[FulfillmentOrder]
    id: UUID
    fulfillment_order_number: str
    order_id: UUID
    warehouse_id: UUID
    carrier_id: UUID | None
    status: FulfillmentOrderStatus
    fulfillment_method: FulfillmentMethod
    carrier_type: CarrierType | None
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

    # Signature
    pickup_signature: str | None
    pickup_timestamp: datetime | None
    pickup_customer_name: str | None
    driver_name: str | None

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
            pickup_signature=model.pickup_signature,
            pickup_timestamp=model.pickup_timestamp,
            pickup_customer_name=model.pickup_customer_name,
            driver_name=model.driver_name,
        )

    @strawberry.field
    async def warehouse_name(self) -> str:
        warehouse = await self._instance.awaitable_attrs.warehouse
        return warehouse.name if warehouse else ""

    @strawberry.field
    async def carrier_name(self) -> str | None:
        carrier = await self._instance.awaitable_attrs.carrier
        return carrier.name if carrier else None

    @strawberry.field
    async def order_number(self) -> str:
        """Get the sales order number from the related Order."""
        order = await self._instance.awaitable_attrs.order
        return order.order_number if order else ""

    @strawberry.field
    async def customer_name(self) -> str:
        """Get the customer name from the related Order."""
        order = await self._instance.awaitable_attrs.order
        if order:
            customer = await order.awaitable_attrs.sold_to_customer
            return customer.company_name if customer else ""
        return ""

    @strawberry.field
    async def ship_to_address(self) -> ShipToAddressResponse | None:
        addr = self._instance.ship_to_address
        if not addr:
            return None
        return ShipToAddressResponse(
            street=addr.get("street"),
            city=addr.get("city"),
            state=addr.get("state"),
            postal_code=addr.get("postal_code"),
            country=addr.get("country"),
        )

    @strawberry.field
    async def line_items(self) -> list[FulfillmentOrderLineItemResponse]:
        items = await self._instance.awaitable_attrs.line_items
        return FulfillmentOrderLineItemResponse.from_orm_model_list(items)

    @strawberry.field
    async def packing_boxes(self) -> list[PackingBoxResponse]:
        boxes = await self._instance.awaitable_attrs.packing_boxes
        return PackingBoxResponse.from_orm_model_list(boxes)

    @strawberry.field
    async def assignments(self) -> list[FulfillmentAssignmentResponse]:
        assignments = await self._instance.awaitable_attrs.assignments
        return FulfillmentAssignmentResponse.from_orm_model_list(assignments)

    @strawberry.field
    async def activities(self) -> list[FulfillmentActivityResponse]:
        activities = await self._instance.awaitable_attrs.activities
        return FulfillmentActivityResponse.from_orm_model_list(activities)


@strawberry.type
class FulfillmentStatsResponse:
    pending_count: int
    in_progress_count: int
    completed_count: int
    backorder_count: int
