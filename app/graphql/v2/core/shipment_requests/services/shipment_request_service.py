import uuid
from datetime import datetime
from uuid import UUID

from commons.db.v6.warehouse.shipment_requests.shipment_request import (
    ShipmentMethod,
    ShipmentPriority,
    ShipmentRequest,
    ShipmentRequestStatus,
)
from commons.db.v6.warehouse.shipment_requests.shipment_request_item import (
    ShipmentRequestItem,
)

from app.core.constants import DEFAULT_QUERY_LIMIT, DEFAULT_QUERY_OFFSET
from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.shipment_requests.repositories.shipment_request_repository import (
    ShipmentRequestRepository,
)
from app.graphql.v2.core.shipment_requests.strawberry.shipment_request_input import (
    ShipmentRequestItemInput,
)


class ShipmentRequestService:
    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        repository: ShipmentRequestRepository,
    ) -> None:
        self.repository = repository

    async def list_by_warehouse(
        self,
        warehouse_id: UUID,
        status: ShipmentRequestStatus | None = None,
        limit: int = DEFAULT_QUERY_LIMIT,
        offset: int = DEFAULT_QUERY_OFFSET,
    ) -> list[ShipmentRequest]:
        return await self.repository.find_by_warehouse(
            warehouse_id=warehouse_id,
            status=status,
            limit=limit,
            offset=offset,
        )

    async def update_status(
        self,
        request_id: UUID,
        status: ShipmentRequestStatus,
        notes: str | None = None,
    ) -> ShipmentRequest:
        request = await self.repository.get_by_id(request_id)
        if not request:
            raise NotFoundError(f"ShipmentRequest with id {request_id} not found")

        request.status = status
        if notes is not None:
            request.notes = notes

        return await self.repository.update(request)

    async def update(
        self,
        request_id: UUID,
        factory_id: UUID | None = None,
        priority: ShipmentPriority | None = None,
        method: ShipmentMethod | None = None,
        status: ShipmentRequestStatus | None = None,
        notes: str | None = None,
        items: list[ShipmentRequestItemInput] | None = None,
    ) -> ShipmentRequest:
        request = await self.repository.get_by_id(request_id)
        if not request:
            raise NotFoundError(f"ShipmentRequest with id {request_id} not found")

        if factory_id is not None:
            request.factory_id = factory_id
        if priority is not None:
            request.priority = priority
        if method is not None:
            request.method = method
        if status is not None:
            request.status = status
        if notes is not None:
            request.notes = notes

        if items is not None:
            # Replace existing items with new ones
            # SQLAlchemy will handle deleting orphans due to cascade="all, delete-orphan"
            request.items = [
                ShipmentRequestItem(
                    request_id=request.id,
                    product_id=item_input.product_id,
                    quantity=item_input.quantity,
                )
                for item_input in items
            ]

        return await self.repository.update(request)

    async def create(
        self,
        warehouse_id: UUID,
        factory_id: UUID,
        request_date: datetime,
        priority: ShipmentPriority,
        method: ShipmentMethod | None,
        status: ShipmentRequestStatus,
        notes: str | None,
        items: list[ShipmentRequestItemInput],
    ) -> ShipmentRequest:
        request_number = await self.generate_request_number()

        # Ensure request_date is naive (no timezone) for DateTime(timezone=False) column
        if request_date and request_date.tzinfo:
            request_date = request_date.replace(tzinfo=None)

        request = ShipmentRequest(
            request_number=request_number,
            warehouse_id=warehouse_id,
            factory_id=factory_id,
            request_date=request_date,
            priority=priority,
            method=method,
            status=status,
            notes=notes,
        )

        for item_input in items:
            request.items.append(
                ShipmentRequestItem(
                    product_id=item_input.product_id,
                    quantity=item_input.quantity,
                    request_id=request.id,
                )
            )

        return await self.repository.create(request)

    async def generate_request_number(self) -> str:
        # Simple generation strategy: SR-{YYYY}-{RANDOM/SEQ}
        year = datetime.now().year
        # Using 8 chars of UUID for uniqueness without DB locking
        unique_suffix = uuid.uuid4().hex[:8].upper()
        return f"SR-{year}-{unique_suffix}"
