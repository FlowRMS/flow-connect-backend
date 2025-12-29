from uuid import UUID

from commons.db.v6.crm.shipment_requests.shipment_request import (
    ShipmentRequest,
    ShipmentRequestStatus,
)

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.shipment_requests.repositories.shipment_request_repository import (
    ShipmentRequestRepository,
)


class ShipmentRequestService:
    def __init__(
        self,
        repository: ShipmentRequestRepository,
    ) -> None:
        self.repository = repository

    async def list_by_warehouse(
        self,
        warehouse_id: UUID,
        status: ShipmentRequestStatus | None = None,
        limit: int = 100,
        offset: int = 0,
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
