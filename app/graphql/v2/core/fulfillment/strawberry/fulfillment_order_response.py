"""Full response type for fulfillment orders - used for detail views."""

from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import FulfillmentOrder

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.fulfillment.strawberry.enums import (
    CarrierType,
    FulfillmentMethod,
    FulfillmentOrderStatus,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_activity_response import (
    FulfillmentActivityResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_assignment_response import (
    FulfillmentAssignmentResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_document_response import (
    FulfillmentDocumentResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.fulfillment_line_item_lite_response import (
    FulfillmentOrderLineItemLiteResponse,
)
from app.graphql.v2.core.fulfillment.strawberry.packing_box_response import (
    PackingBoxResponse,
)


@strawberry.type
class ShipToAddressResponse:
    name: str | None = None
    street: str | None = None
    street_line_2: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None
    phone: str | None = None


@strawberry.type
class FulfillmentOrderResponse(DTOMixin[FulfillmentOrder]):
    """Full response for detail views - includes nested collections."""

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
            pickup_signature=model.pickup_signature,
            pickup_timestamp=model.pickup_timestamp,
            pickup_customer_name=model.pickup_customer_name,
            driver_name=model.driver_name,
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

    @strawberry.field
    def ship_to_address(self) -> ShipToAddressResponse | None:
        """Get ship-to address - relationship is eager-loaded."""
        address = self._instance.ship_to_address
        if not address:
            return None
        return ShipToAddressResponse(
            name=self._instance.ship_to_name,
            street=address.line_1,
            street_line_2=address.line_2,
            city=address.city,
            state=address.state,
            postal_code=address.zip_code,
            country=address.country,
            phone=self._instance.ship_to_phone,
        )

    @strawberry.field
    def line_items(self) -> list[FulfillmentOrderLineItemLiteResponse]:
        """Get line items - relationship is eager-loaded."""
        return FulfillmentOrderLineItemLiteResponse.from_orm_model_list(
            self._instance.line_items
        )

    @strawberry.field
    def packing_boxes(self) -> list[PackingBoxResponse]:
        """Get packing boxes - relationship is eager-loaded."""
        return PackingBoxResponse.from_orm_model_list(self._instance.packing_boxes)

    @strawberry.field
    def assignments(self) -> list[FulfillmentAssignmentResponse]:
        """Get assignments - relationship is eager-loaded."""
        return FulfillmentAssignmentResponse.from_orm_model_list(
            self._instance.assignments
        )

    @strawberry.field
    def documents(self) -> list[FulfillmentDocumentResponse]:
        """Get documents - relationship is eager-loaded."""
        return FulfillmentDocumentResponse.from_orm_model_list(
            self._instance.documents
        )

    @strawberry.field
    def activities(self) -> list[FulfillmentActivityResponse]:
        """Get activities - relationship is eager-loaded."""
        return FulfillmentActivityResponse.from_orm_model_list(
            self._instance.activities
        )
