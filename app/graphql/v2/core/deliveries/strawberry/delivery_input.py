
from datetime import date, datetime, timezone
from uuid import UUID

import strawberry
from commons.db.v6 import (
    Delivery,
    DeliveryAssignee,
    DeliveryDocument,
    DeliveryIssue,
    DeliveryItem,
    DeliveryItemReceipt,
    DeliveryStatusHistory,
    RecurringShipment,
    WarehouseMemberRole,
)
from commons.db.v6.warehouse.deliveries.delivery_enums import (
    DeliveryDocumentType,
    DeliveryIssueStatus,
    DeliveryIssueType,
    DeliveryItemStatus,
    DeliveryReceiptType,
    DeliveryStatus,
    RecurringShipmentStatus,
)

from app.core.strawberry.inputs import BaseInputGQL

from .delivery_enums import (
    DeliveryAssigneeRoleGQL,
    DeliveryDocumentTypeGQL,
    DeliveryIssueStatusGQL,
    DeliveryIssueTypeGQL,
    DeliveryItemStatusGQL,
    DeliveryReceiptTypeGQL,
    DeliveryStatusGQL,
    RecurringShipmentStatusGQL,
)


@strawberry.input
class DeliveryInput(BaseInputGQL[Delivery]):
    """Input type for creating/updating deliveries."""

    po_number: str
    warehouse_id: UUID
    vendor_id: UUID
    carrier_id: UUID | None = None
    tracking_number: str | None = None
    status: DeliveryStatusGQL = DeliveryStatusGQL.DRAFT
    expected_date: date | None = None
    arrived_at: datetime | None = None
    receiving_started_at: datetime | None = None
    received_at: datetime | None = None
    origin_address_id: UUID | None = None
    destination_address_id: UUID | None = None
    recurring_shipment_id: UUID | None = None
    vendor_contact_name: str | None = None
    vendor_contact_email: str | None = None
    notes: str | None = None
    updated_by_id: UUID | None = None

    def to_orm_model(self) -> Delivery:
        return Delivery(
            po_number=self.po_number,
            warehouse_id=self.warehouse_id,
            vendor_id=self.vendor_id,
            carrier_id=self.carrier_id,
            tracking_number=self.tracking_number,
            status=DeliveryStatus(self.status.value),
            expected_date=self.expected_date,
            arrived_at=self.arrived_at,
            receiving_started_at=self.receiving_started_at,
            received_at=self.received_at,
            origin_address_id=self.origin_address_id,
            destination_address_id=self.destination_address_id,
            recurring_shipment_id=self.recurring_shipment_id,
            vendor_contact_name=self.vendor_contact_name,
            vendor_contact_email=self.vendor_contact_email,
            notes=self.notes,
            updated_by_id=self.updated_by_id,
        )


@strawberry.input
class DeliveryItemInput(BaseInputGQL[DeliveryItem]):
    """Input type for creating/updating delivery items."""

    delivery_id: UUID
    product_id: UUID
    expected_quantity: int = 0
    received_quantity: int = 0
    damaged_quantity: int = 0
    status: DeliveryItemStatusGQL = DeliveryItemStatusGQL.PENDING
    discrepancy_notes: str | None = None

    def to_orm_model(self) -> DeliveryItem:
        return DeliveryItem(
            delivery_id=self.delivery_id,
            product_id=self.product_id,
            expected_quantity=self.expected_quantity,
            received_quantity=self.received_quantity,
            damaged_quantity=self.damaged_quantity,
            status=DeliveryItemStatus(self.status.value),
            discrepancy_notes=self.discrepancy_notes,
        )


@strawberry.input
class DeliveryItemReceiptInput(BaseInputGQL[DeliveryItemReceipt]):
    """Input type for creating/updating delivery item receipts."""

    delivery_item_id: UUID
    receipt_type: DeliveryReceiptTypeGQL = DeliveryReceiptTypeGQL.RECEIPT
    received_quantity: int = 0
    damaged_quantity: int = 0
    location_id: UUID | None = None
    received_by_id: UUID | None = None
    received_at: datetime | None = None
    note: str | None = None

    def to_orm_model(self) -> DeliveryItemReceipt:
        return DeliveryItemReceipt(
            delivery_item_id=self.delivery_item_id,
            receipt_type=DeliveryReceiptType(self.receipt_type.value),
            received_quantity=self.received_quantity,
            damaged_quantity=self.damaged_quantity,
            location_id=self.location_id,
            received_by_id=self.received_by_id,
            received_at=self.received_at,
            note=self.note,
        )


@strawberry.input
class DeliveryStatusHistoryInput(BaseInputGQL[DeliveryStatusHistory]):
    """Input type for creating delivery status history entries."""

    delivery_id: UUID
    status: DeliveryStatusGQL
    timestamp: datetime | None = None
    user_id: UUID | None = None
    note: str | None = None

    def to_orm_model(self) -> DeliveryStatusHistory:
        return DeliveryStatusHistory(
            delivery_id=self.delivery_id,
            status=DeliveryStatus(self.status.value),
            timestamp=self.timestamp or datetime.now(timezone.utc),
            user_id=self.user_id,
            note=self.note,
        )


@strawberry.input
class DeliveryIssueInput(BaseInputGQL[DeliveryIssue]):
    """Input type for creating/updating delivery issues."""

    delivery_id: UUID
    delivery_item_id: UUID
    receipt_id: UUID | None = None
    issue_type: DeliveryIssueTypeGQL
    custom_issue_type: str | None = None
    quantity: int = 0
    status: DeliveryIssueStatusGQL = DeliveryIssueStatusGQL.OPEN
    description: str | None = None
    notes: str | None = None
    communicated_at: datetime | None = None

    def to_orm_model(self) -> DeliveryIssue:
        return DeliveryIssue(
            delivery_id=self.delivery_id,
            delivery_item_id=self.delivery_item_id,
            receipt_id=self.receipt_id,
            issue_type=DeliveryIssueType(self.issue_type.value),
            custom_issue_type=self.custom_issue_type,
            quantity=self.quantity,
            status=DeliveryIssueStatus(self.status.value),
            description=self.description,
            notes=self.notes,
            communicated_at=self.communicated_at,
        )


@strawberry.input
class DeliveryDocumentInput(BaseInputGQL[DeliveryDocument]):
    """Input type for creating/updating delivery documents."""

    delivery_id: UUID
    file_id: UUID
    name: str
    doc_type: DeliveryDocumentTypeGQL
    file_url: str
    mime_type: str
    file_size: int | None = None
    uploaded_by_id: UUID | None = None
    notes: str | None = None

    def to_orm_model(self) -> DeliveryDocument:
        return DeliveryDocument(
            delivery_id=self.delivery_id,
            file_id=self.file_id,
            name=self.name,
            doc_type=DeliveryDocumentType(self.doc_type.value),
            file_url=self.file_url,
            mime_type=self.mime_type,
            file_size=self.file_size,
            uploaded_by_id=self.uploaded_by_id,
            notes=self.notes,
        )


@strawberry.input
class DeliveryAssigneeInput(BaseInputGQL[DeliveryAssignee]):
    """Input type for assigning users to deliveries."""

    delivery_id: UUID
    user_id: UUID
    role: DeliveryAssigneeRoleGQL

    def to_orm_model(self) -> DeliveryAssignee:
        return DeliveryAssignee(
            delivery_id=self.delivery_id,
            user_id=self.user_id,
            role=WarehouseMemberRole(self.role.value),
        )


@strawberry.input
class RecurringShipmentInput(BaseInputGQL[RecurringShipment]):
    """Input type for creating/updating recurring shipments."""

    name: str
    vendor_id: UUID
    warehouse_id: UUID
    recurrence_pattern: strawberry.scalars.JSON
    start_date: date
    vendor_contact_name: str | None = None
    vendor_contact_email: str | None = None
    carrier: str | None = None
    notes: str | None = None
    end_date: date | None = None
    status: RecurringShipmentStatusGQL = RecurringShipmentStatusGQL.ACTIVE
    last_generated_date: date | None = None
    next_expected_date: date | None = None
    updated_by_id: UUID | None = None

    def to_orm_model(self) -> RecurringShipment:
        return RecurringShipment(
            name=self.name,
            vendor_id=self.vendor_id,
            warehouse_id=self.warehouse_id,
            recurrence_pattern=dict(self.recurrence_pattern),
            start_date=self.start_date,
            vendor_contact_name=self.vendor_contact_name,
            vendor_contact_email=self.vendor_contact_email,
            carrier=self.carrier,
            notes=self.notes,
            end_date=self.end_date,
            status=RecurringShipmentStatus(self.status.value),
            last_generated_date=self.last_generated_date,
            next_expected_date=self.next_expected_date,
            updated_by_id=self.updated_by_id,
        )
