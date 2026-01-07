from decimal import Decimal
from uuid import UUID

from commons.db.v6 import LocationProductAssignment

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.warehouses.repositories import (
    LocationProductAssignmentRepository,
    WarehouseLocationRepository,
)


class WarehouseLocationAssignmentService:
    def __init__(
        self,
        assignment_repository: LocationProductAssignmentRepository,
        location_repository: WarehouseLocationRepository,
    ) -> None:
        super().__init__()
        self.assignment_repository = assignment_repository
        self.location_repository = location_repository

    async def assign_product(
        self, location_id: UUID, product_id: UUID, quantity: Decimal
    ) -> LocationProductAssignment:
        location = await self.location_repository.get_by_id(location_id)
        if not location:
            raise NotFoundError(f"Location with id {location_id} not found")

        existing = await self.assignment_repository.get_by_location_and_product(
            location_id, product_id
        )
        if existing:
            existing.quantity = quantity
            return await self.assignment_repository.update(existing)

        assignment = LocationProductAssignment(
            location_id=location_id,
            product_id=product_id,
            quantity=quantity,
        )
        return await self.assignment_repository.create(assignment)

    async def update_product_quantity(
        self, location_id: UUID, product_id: UUID, quantity: Decimal
    ) -> LocationProductAssignment:
        assignment = await self.assignment_repository.get_by_location_and_product(
            location_id, product_id
        )
        if not assignment:
            raise NotFoundError(
                f"Product {product_id} is not assigned to location {location_id}"
            )
        assignment.quantity = quantity
        return await self.assignment_repository.update(assignment)

    async def remove_product(self, location_id: UUID, product_id: UUID) -> bool:
        return await self.assignment_repository.delete_by_location_and_product(
            location_id, product_id
        )

    async def get_assignments_by_location(
        self, location_id: UUID
    ) -> list[LocationProductAssignment]:
        return await self.assignment_repository.list_by_location(location_id)

    async def get_assignments_by_product(
        self, product_id: UUID
    ) -> list[LocationProductAssignment]:
        return await self.assignment_repository.list_by_product(product_id)
