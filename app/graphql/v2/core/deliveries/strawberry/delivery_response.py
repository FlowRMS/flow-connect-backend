from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import Delivery
from commons.db.v6.warehouse.deliveries.delivery_enums import DeliveryStatus

from app.core.db.adapters.dto import DTOMixin
from app.graphql.v2.core.factories.strawberry.factory_response import (
    FactoryLiteResponse,
)
from app.graphql.v2.core.shipping_carriers.strawberry.shipping_carrier_response import (
    ShippingCarrierResponse,
)

from .delivery_assignee_response import DeliveryAssigneeResponse
from .delivery_document_response import DeliveryDocumentResponse
from .delivery_issue_response import DeliveryIssueResponse
from .delivery_item_response import DeliveryItemResponse
from .delivery_status_history_response import DeliveryStatusHistoryResponse


@strawberry.type
class DeliveryLiteResponse(DTOMixin[Delivery]):
    """Lite response type for deliveries"""

    _instance: strawberry.Private[Delivery]
    id: UUID
    po_number: str
    warehouse_id: UUID
    vendor_id: UUID
    carrier_id: UUID | None
    tracking_number: str | None
    status: DeliveryStatus
    expected_date: date | None
    arrived_at: datetime | None
    receiving_started_at: datetime | None
    received_at: datetime | None
    origin_address_id: UUID | None
    destination_address_id: UUID | None
    recurring_shipment_id: UUID | None
    vendor_contact_name: str | None
    vendor_contact_email: str | None
    notes: str | None
    created_at: datetime
    created_by_id: UUID | None
    updated_by_id: UUID | None
    updated_at: datetime | None

    @classmethod
    def from_orm_model(cls, model: Delivery) -> Self:
        return cls(
            _instance=model,
            id=model.id,
            po_number=model.po_number,
            warehouse_id=model.warehouse_id,
            vendor_id=model.vendor_id,
            carrier_id=model.carrier_id,
            tracking_number=model.tracking_number,
            status=model.status,
            expected_date=model.expected_date,
            arrived_at=model.arrived_at,
            receiving_started_at=model.receiving_started_at,
            received_at=model.received_at,
            origin_address_id=model.origin_address_id,
            destination_address_id=model.destination_address_id,
            recurring_shipment_id=model.recurring_shipment_id,
            vendor_contact_name=model.vendor_contact_name,
            vendor_contact_email=model.vendor_contact_email,
            notes=model.notes,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
            updated_by_id=model.updated_by_id,
            updated_at=model.updated_at,
        )


@strawberry.type
class DeliveryResponse(DeliveryLiteResponse):
    """Full response type for deliveries - includes relations (pre-loaded via repository)."""

    @strawberry.field
    def items(self) -> list[DeliveryItemResponse]:
        """Delivery items - pre-loaded via repository."""
        return DeliveryItemResponse.from_orm_model_list(self._instance.items)

    @strawberry.field
    def status_history(self) -> list[DeliveryStatusHistoryResponse]:
        """Status history - pre-loaded via repository."""
        return DeliveryStatusHistoryResponse.from_orm_model_list(
            self._instance.status_history
        )

    @strawberry.field
    def issues(self) -> list[DeliveryIssueResponse]:
        """Delivery issues - pre-loaded via repository."""
        return DeliveryIssueResponse.from_orm_model_list(self._instance.issues)

    @strawberry.field
    def assignees(self) -> list[DeliveryAssigneeResponse]:
        """Assignees - pre-loaded via repository."""
        return DeliveryAssigneeResponse.from_orm_model_list(self._instance.assignees)

    @strawberry.field
    def documents(self) -> list[DeliveryDocumentResponse]:
        """Documents - pre-loaded via repository."""
        return DeliveryDocumentResponse.from_orm_model_list(self._instance.documents)

    @strawberry.field
    def vendor(self) -> FactoryLiteResponse:
        """Vendor - pre-loaded via repository."""
        return FactoryLiteResponse.from_orm_model(self._instance.vendor)

    @strawberry.field
    def carrier(self) -> ShippingCarrierResponse | None:
        """Carrier - pre-loaded via repository."""
        return ShippingCarrierResponse.from_orm_model_optional(self._instance.carrier)
