from datetime import date, datetime
from uuid import UUID

import strawberry
from commons.db.v6 import Delivery
from commons.db.v6.warehouse.deliveries.delivery_enums import DeliveryStatus

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class DeliveryInput(BaseInputGQL[Delivery]):
    """Input type for creating/updating deliveries."""

    po_number: str
    warehouse_id: UUID
    vendor_id: UUID
    carrier_id: UUID | None = None
    tracking_number: str | None = None
    status: DeliveryStatus = DeliveryStatus.DRAFT
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
            status=self.status,
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
