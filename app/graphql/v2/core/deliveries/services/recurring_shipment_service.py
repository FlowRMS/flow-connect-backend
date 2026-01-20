
from datetime import date
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import RecurringShipment

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.deliveries.repositories.recurring_shipments_repository import (
    RecurringShipmentsRepository,
)
from app.graphql.v2.core.deliveries.strawberry.inputs import RecurringShipmentInput
from app.graphql.v2.core.deliveries.utils.recurrence_utils import calculate_next_date


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
        """
        Create a recurring shipment with auto-calculated next_expected_date.

        The backend now calculates the next occurrence date instead of relying
        on the frontend to send it.

        Note: Recurrence pattern validation is handled by the repository preprocessor.

        Args:
            input: RecurringShipmentInput with pattern and dates

        Returns:
            Created recurring shipment with calculated next_expected_date
        """
        # Convert input to ORM model
        shipment = input.to_orm_model()

        # Calculate next_expected_date from start_date
        # If start_date is in the future, use it; otherwise calculate next from today
        today = date.today()
        if shipment.start_date >= today:
            shipment.next_expected_date = shipment.start_date
        else:
            shipment.next_expected_date = calculate_next_date(
                shipment.recurrence_pattern, shipment.start_date
            )

        # last_generated_date is None initially (no deliveries generated yet)
        shipment.last_generated_date = None

        return await self.repository.create(shipment)

    async def update(
        self, shipment_id: UUID, input: RecurringShipmentInput
    ) -> RecurringShipment:
        """
        Update a recurring shipment with auto-recalculation of next_expected_date.

        If the recurrence pattern or start_date changes, recalculates next_expected_date.

        Note: Recurrence pattern validation is handled by the repository preprocessor.

        Args:
            shipment_id: ID of shipment to update
            input: Updated shipment data

        Returns:
            Updated recurring shipment

        Raises:
            NotFoundError: If shipment not found
        """
        if not await self.repository.exists(shipment_id):
            raise NotFoundError(
                f"Recurring shipment with id {shipment_id} not found"
            )

        # Get existing shipment to check if pattern/dates changed
        existing = await self.repository.get_by_id(shipment_id)

        shipment = input.to_orm_model()
        shipment.id = shipment_id

        # Recalculate next_expected_date if pattern or start_date changed
        pattern_changed = (
            input.recurrence_pattern
            and input.recurrence_pattern != existing.recurrence_pattern
        )
        start_date_changed = (
            input.start_date and input.start_date != existing.start_date
        )

        if pattern_changed or start_date_changed:
            # Use last_generated_date if available, otherwise start_date
            base_date = shipment.last_generated_date or shipment.start_date
            shipment.next_expected_date = calculate_next_date(
                shipment.recurrence_pattern, base_date
            )
        elif not input.next_expected_date:
            # If next_expected_date not provided, preserve existing
            shipment.next_expected_date = existing.next_expected_date

        return await self.repository.update(shipment)

    async def delete(self, shipment_id: UUID) -> bool:
        if not await self.repository.exists(shipment_id):
            raise NotFoundError(
                f"Recurring shipment with id {shipment_id} not found"
            )
        return await self.repository.delete(shipment_id)
