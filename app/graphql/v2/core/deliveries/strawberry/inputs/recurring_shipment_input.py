from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6 import RecurringShipment
from commons.db.v6.warehouse.deliveries.delivery_enums import RecurringShipmentStatus

from app.core.strawberry.inputs import BaseInputGQL


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
    status: RecurringShipmentStatus = RecurringShipmentStatus.ACTIVE
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
            status=self.status,
            last_generated_date=self.last_generated_date,
            next_expected_date=self.next_expected_date,
            updated_by_id=self.updated_by_id,
        )
