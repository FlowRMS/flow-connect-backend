
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import RecurringShipment

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.recurring_shipments_repository import (
    RecurringShipmentsRepository,
)
from app.graphql.v2.core.deliveries.strawberry.delivery_input import (
    RecurringShipmentInput,
)


class RecurringShipmentService:
    """Service for recurring shipment operations."""

    def __init__(
        self,
        repository: RecurringShipmentsRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.auth_info = auth_info

    async def get_by_id(self, shipment_id: UUID) -> RecurringShipment:
        shipment = await self.repository.get_by_id(shipment_id)
        if not shipment:
            raise NotFoundError(
                f"Recurring shipment with id {shipment_id} not found"
            )
        return shipment

    async def list_all(self) -> list[RecurringShipment]:
        return await self.repository.list_all()

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[RecurringShipment]:
        return await self.repository.list_by_warehouse(warehouse_id)

    async def create(self, input: RecurringShipmentInput) -> RecurringShipment:
        return await self.repository.create(input.to_orm_model())

    async def update(
        self, shipment_id: UUID, input: RecurringShipmentInput
    ) -> RecurringShipment:
        if not await self.repository.exists(shipment_id):
            raise NotFoundError(
                f"Recurring shipment with id {shipment_id} not found"
            )
        shipment = input.to_orm_model()
        shipment.id = shipment_id
        return await self.repository.update(shipment)

    async def delete(self, shipment_id: UUID) -> bool:
        if not await self.repository.exists(shipment_id):
            raise NotFoundError(
                f"Recurring shipment with id {shipment_id} not found"
            )
        return await self.repository.delete(shipment_id)
