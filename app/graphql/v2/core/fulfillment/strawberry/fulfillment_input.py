from datetime import date
from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import (
    CarrierType,
    FulfillmentAssignmentRole,
    FulfillmentMethod,
    FulfillmentOrder,
    FulfillmentOrderLineItem,
    PackingBox,
)

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class ShipToAddressInput:
    street: str | None = None
    city: str | None = None
    state: str | None = None
    postal_code: str | None = None
    country: str | None = None

    def to_dict(self) -> dict:
        return {
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
        }


@strawberry.input
class CreateFulfillmentOrderInput(BaseInputGQL[FulfillmentOrder]):
    order_id: UUID
    warehouse_id: UUID
    fulfillment_method: FulfillmentMethod = FulfillmentMethod.SHIP
    carrier_id: UUID | None = None
    carrier_type: CarrierType | None = None
    ship_to_address: ShipToAddressInput | None = None
    need_by_date: date | None = None

    def to_orm_model(self) -> FulfillmentOrder:
        return FulfillmentOrder(
            order_id=self.order_id,
            warehouse_id=self.warehouse_id,
            fulfillment_order_number="",  # Will be generated
            fulfillment_method=self.fulfillment_method,
            carrier_id=self.carrier_id,
            carrier_type=self.carrier_type,
            ship_to_address=self.ship_to_address.to_dict()
            if self.ship_to_address
            else None,
            need_by_date=self.need_by_date,
        )


@strawberry.input
class UpdateFulfillmentOrderInput:
    warehouse_id: UUID | None = strawberry.UNSET
    carrier_id: UUID | None = strawberry.UNSET
    carrier_type: CarrierType | None = strawberry.UNSET
    ship_to_address: ShipToAddressInput | None = strawberry.UNSET
    need_by_date: date | None = strawberry.UNSET
    hold_reason: str | None = strawberry.UNSET


@strawberry.input
class CreateFulfillmentLineItemInput(BaseInputGQL[FulfillmentOrderLineItem]):
    product_id: UUID
    ordered_qty: Decimal
    order_detail_id: UUID | None = None

    def to_orm_model(self) -> FulfillmentOrderLineItem:
        return FulfillmentOrderLineItem(
            product_id=self.product_id,
            order_detail_id=self.order_detail_id,
            ordered_qty=self.ordered_qty,
        )


@strawberry.input
class UpdatePickedQuantityInput:
    line_item_id: UUID
    quantity: Decimal
    notes: str | None = None


@strawberry.input
class AssignItemToBoxInput:
    box_id: UUID
    line_item_id: UUID
    quantity: Decimal


@strawberry.input
class CreatePackingBoxInput(BaseInputGQL[PackingBox]):
    container_type_id: UUID | None = None
    length: Decimal | None = None
    width: Decimal | None = None
    height: Decimal | None = None
    weight: Decimal | None = None

    def to_orm_model(self) -> PackingBox:
        return PackingBox(
            container_type_id=self.container_type_id,
            box_number=0,  # Will be set by service
            length=self.length,
            width=self.width,
            height=self.height,
            weight=self.weight,
        )


@strawberry.input
class UpdatePackingBoxInput:
    container_type_id: UUID | None = strawberry.UNSET
    length: Decimal | None = strawberry.UNSET
    width: Decimal | None = strawberry.UNSET
    height: Decimal | None = strawberry.UNSET
    weight: Decimal | None = strawberry.UNSET
    tracking_number: str | None = strawberry.UNSET


@strawberry.input
class CompleteShippingInput:
    tracking_numbers: list[str] | None = None
    bol_number: str | None = None
    pro_number: str | None = None
    signature: str | None = None
    driver_name: str | None = None
    pickup_customer_name: str | None = None


@strawberry.input
class BulkAssignmentInput:
    fulfillment_order_ids: list[UUID]
    manager_ids: list[UUID] | None = None
    worker_ids: list[UUID] | None = None


@strawberry.input
class AssignUserInput:
    user_id: UUID
    role: FulfillmentAssignmentRole


@strawberry.input
class AddAssignmentInput:
    """Input for adding an assignment to a fulfillment order."""

    fulfillment_order_id: UUID
    user_id: UUID
    role: FulfillmentAssignmentRole


@strawberry.input
class MarkManufacturerFulfilledInput:
    """Input for marking line items as manufacturer fulfilled."""

    fulfillment_order_id: UUID
    line_item_ids: list[UUID]


@strawberry.input
class SplitLineItemInput:
    """Input for splitting a line item between warehouse and manufacturer."""

    line_item_id: UUID
    warehouse_qty: Decimal
    manufacturer_qty: Decimal


@strawberry.input
class CancelBackorderInput:
    """Input for cancelling backorder items."""

    fulfillment_order_id: UUID
    line_item_ids: list[UUID]
    reason: str
