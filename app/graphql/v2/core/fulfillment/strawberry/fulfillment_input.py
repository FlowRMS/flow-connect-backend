from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

import strawberry
from commons.db.v6.fulfillment import (
    CarrierType,
    FulfillmentAssignmentRole,
    FulfillmentDocumentType,
    FulfillmentMethod,
    FulfillmentOrder,
    FulfillmentOrderLineItem,
    PackingBox,
)
from strawberry.file_uploads import Upload

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.addresses.strawberry.address_input import AddressInput


@strawberry.input
class CreateFulfillmentOrderInput(BaseInputGQL[FulfillmentOrder]):
    order_id: UUID
    warehouse_id: UUID
    fulfillment_method: FulfillmentMethod = FulfillmentMethod.SHIP
    carrier_id: UUID | None = None
    carrier_type: CarrierType | None = None
    ship_to_address: AddressInput | None = None
    ship_to_name: str | None = None
    ship_to_phone: str | None = None
    need_by_date: date | None = None

    def to_orm_model(self) -> FulfillmentOrder:
        order = FulfillmentOrder(
            fulfillment_method=self.fulfillment_method,
            carrier_type=self.carrier_type,
            need_by_date=self.need_by_date,
        )
        order.fulfillment_order_number = ""  # Will be generated
        order.order_id = self.order_id
        order.warehouse_id = self.warehouse_id
        order.carrier_id = self.carrier_id
        # ship_to_address is handled by the service layer
        return order


@strawberry.input
class UpdateFulfillmentOrderInput:
    warehouse_id: UUID | None = strawberry.UNSET
    fulfillment_method: FulfillmentMethod | None = strawberry.UNSET
    carrier_id: UUID | None = strawberry.UNSET
    carrier_type: CarrierType | None = strawberry.UNSET
    freight_class: str | None = strawberry.UNSET
    ship_to_address: AddressInput | None = strawberry.UNSET
    ship_to_name: str | None = strawberry.UNSET
    ship_to_phone: str | None = strawberry.UNSET
    need_by_date: date | None = strawberry.UNSET
    hold_reason: str | None = strawberry.UNSET


@strawberry.input
class CreateFulfillmentLineItemInput(BaseInputGQL[FulfillmentOrderLineItem]):
    product_id: UUID
    ordered_qty: Decimal
    order_detail_id: UUID | None = None

    def to_orm_model(self) -> FulfillmentOrderLineItem:
        item = FulfillmentOrderLineItem(
            ordered_qty=self.ordered_qty,
        )
        item.product_id = self.product_id
        item.order_detail_id = self.order_detail_id
        return item


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
        box = PackingBox(
            length=self.length,
            width=self.width,
            height=self.height,
            weight=self.weight,
        )
        box.container_type_id = self.container_type_id
        box.box_number = 0  # Will be set by service
        return box


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


@strawberry.input
class AddDocumentInput:
    """Input for adding a document to a fulfillment order."""

    fulfillment_order_id: UUID
    document_type: FulfillmentDocumentType
    file_name: str
    file_url: str
    file_size: int | None = None
    mime_type: str | None = None
    notes: str | None = None


@strawberry.input
class UploadDocumentInput:
    """Input for uploading a document file to a fulfillment order."""

    fulfillment_order_id: UUID
    document_type: FulfillmentDocumentType
    file: Upload
    notes: Optional[str] = None
