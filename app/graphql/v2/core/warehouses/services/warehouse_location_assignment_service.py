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
            _ = await self.assignment_repository.update(existing)
            # Reload with product relationship for response
            return await self.assignment_repository.get_with_product(existing.id)

        assignment = LocationProductAssignment(
            location_id=location_id,
            product_id=product_id,
            quantity=quantity,
        )
        created = await self.assignment_repository.create(assignment)
        # Reload with product relationship for response
        return await self.assignment_repository.get_with_product(created.id)

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
        _ = await self.assignment_repository.update(assignment)
        # Reload with product relationship for response
        return await self.assignment_repository.get_with_product(assignment.id)

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

    async def bulk_assign_products(
        self,
        assignments: list[tuple[UUID, UUID, Decimal]],
    ) -> list[LocationProductAssignment]:
        """Bulk assign products to locations in a single transaction.

        Optimized to use batch queries instead of N+1 individual queries.

        Args:
            assignments: List of (location_id, product_id, quantity) tuples

        Returns:
            List of created/updated assignments with product details loaded
        """
        if not assignments:
            return []

        # 1. Batch fetch all existing assignments (single query)
        pairs = [(loc_id, prod_id) for loc_id, prod_id, _ in assignments]
        existing_map = await self.assignment_repository.get_by_location_product_pairs(
            pairs
        )

        # 2. Process updates and creates
        result_ids: list[UUID] = []
        for location_id, product_id, quantity in assignments:
            key = (location_id, product_id)
            if key in existing_map:
                # Update existing
                existing = existing_map[key]
                existing.quantity = quantity
                result_ids.append(existing.id)
            else:
                # Create new
                assignment = LocationProductAssignment(
                    location_id=location_id,
                    product_id=product_id,
                    quantity=quantity,
                )
                self.assignment_repository.session.add(assignment)
                result_ids.append(assignment.id)

        # 3. Flush all changes at once
        await self.assignment_repository.session.flush()

        # 4. Batch load all results with product relationship (single query)
        return await self.assignment_repository.get_many_with_product(result_ids)

    async def bulk_remove_products(
        self,
        removals: list[tuple[UUID, UUID]],
    ) -> int:
        """Bulk remove products from locations in a single transaction.

        Optimized to use a single DELETE query instead of N individual queries.

        Args:
            removals: List of (location_id, product_id) tuples

        Returns:
            Number of assignments successfully removed
        """
        if not removals:
            return 0

        # Single bulk delete query
        return await self.assignment_repository.bulk_delete_by_location_product_pairs(
            removals
        )
