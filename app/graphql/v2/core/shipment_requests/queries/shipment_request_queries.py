from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.warehouse.shipment_requests import ShipmentRequestStatus

from app.graphql.inject import inject
from app.graphql.v2.core.shipment_requests.services.shipment_request_service import (
    ShipmentRequestService,
)
from app.graphql.v2.core.shipment_requests.strawberry.shipment_request_response import (
    ShipmentRequestResponse,
)


@strawberry.type
class ShipmentRequestStatusOption:
    label: str
    value: str


@strawberry.type
class ShipmentRequestQueries:
    @strawberry.field
    def shipment_request_statuses(self) -> list[ShipmentRequestStatusOption]:
        return [
            ShipmentRequestStatusOption(label=status.name.replace("_", " ").title(), value=status.name)
            for status in ShipmentRequestStatus
        ]

    @strawberry.field
    @inject
    async def shipment_requests(
        self,
        service: Injected[ShipmentRequestService],
        warehouse_id: UUID,
        status: ShipmentRequestStatus | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ShipmentRequestResponse]:
        requests = await service.list_by_warehouse(
            warehouse_id=warehouse_id,
            status=status,
            limit=limit,
            offset=offset,
        )
        return ShipmentRequestResponse.from_orm_model_list(requests)
