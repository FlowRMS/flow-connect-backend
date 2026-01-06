
from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6 import Delivery

from app.core.db.adapters.dto import DTOMixin

from .delivery_assignee_response import DeliveryAssigneeResponse
from .delivery_document_response import DeliveryDocumentResponse
from .delivery_enums import DeliveryStatusGQL
from .delivery_issue_response import DeliveryIssueResponse
from .delivery_item_response import DeliveryItemResponse
from .delivery_status_history_response import DeliveryStatusHistoryResponse


@strawberry.type
class DeliveryResponse(DTOMixin[Delivery]):
    """Response type for deliveries."""

    _instance: strawberry.Private[Delivery]
    id: UUID
    po_number: str
    warehouse_id: UUID
    vendor_id: UUID
    carrier_id: UUID | None
    tracking_number: str | None
    status: DeliveryStatusGQL
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
            status=DeliveryStatusGQL(model.status.value),
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

    @strawberry.field
    async def items(self) -> list[DeliveryItemResponse]:
        items = await self._instance.awaitable_attrs.items
        return DeliveryItemResponse.from_orm_model_list(items)

    @strawberry.field
    async def status_history(self) -> list[DeliveryStatusHistoryResponse]:
        history = await self._instance.awaitable_attrs.status_history
        return DeliveryStatusHistoryResponse.from_orm_model_list(history)

    @strawberry.field
    async def issues(self) -> list[DeliveryIssueResponse]:
        issues = await self._instance.awaitable_attrs.issues
        return DeliveryIssueResponse.from_orm_model_list(issues)

    @strawberry.field
    async def assignees(self) -> list[DeliveryAssigneeResponse]:
        assignees = await self._instance.awaitable_attrs.assignees
        return DeliveryAssigneeResponse.from_orm_model_list(assignees)

    @strawberry.field
    async def documents(self) -> list[DeliveryDocumentResponse]:
        documents = await self._instance.awaitable_attrs.documents
        return DeliveryDocumentResponse.from_orm_model_list(documents)
