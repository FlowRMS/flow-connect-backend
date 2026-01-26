from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import RecurringShipment
from commons.db.v6.warehouse.deliveries.delivery_enums import RecurringShipmentStatus
from strawberry.scalars import JSON

from app.core.db.adapters.dto import DTOMixin


@strawberry.type
class RecurringShipmentResponse(DTOMixin[RecurringShipment]):
    """Response type for recurring shipments."""

    _instance: strawberry.Private[RecurringShipment]
    id: UUID
    name: str
    vendor_id: UUID
    vendor_contact_name: str | None
    vendor_contact_email: str | None
    warehouse_id: UUID
    carrier: str | None
    notes: str | None
    recurrence_pattern: JSON
    start_date: date
    end_date: date | None
    status: RecurringShipmentStatus
    last_generated_date: date | None
    next_expected_date: date | None
    created_at: datetime
    updated_at: datetime | None
    created_by_id: UUID | None
    updated_by_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: RecurringShipment) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            name=model.name,
            vendor_id=model.vendor_id,
            vendor_contact_name=model.vendor_contact_name,
            vendor_contact_email=model.vendor_contact_email,
            warehouse_id=model.warehouse_id,
            carrier=model.carrier,
            notes=model.notes,
            recurrence_pattern=model.recurrence_pattern,
            start_date=model.start_date,
            end_date=model.end_date,
            status=model.status,
            last_generated_date=model.last_generated_date,
            next_expected_date=model.next_expected_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by_id=model.created_by_id,
            updated_by_id=model.updated_by_id,
        )
