from decimal import Decimal
from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.warehouses.services.warehouse_location_assignment_service import (
    WarehouseLocationAssignmentService,
)
from app.graphql.v2.core.warehouses.services.warehouse_location_bulk_service import (
    WarehouseLocationBulkService,
)
from app.graphql.v2.core.warehouses.services.warehouse_location_service import (
    WarehouseLocationService,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_location_input import (
    BulkProductAssignmentInput,
    BulkProductRemovalInput,
    BulkWarehouseLocationInput,
    WarehouseLocationInput,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_location_response import (
    LocationProductAssignmentResponse,
    WarehouseLocationResponse,
)


@strawberry.type
class WarehouseLocationMutations:
    @strawberry.mutation
    @inject
    async def create_warehouse_location(
        self,
        input: WarehouseLocationInput,
        service: Injected[WarehouseLocationService],
    ) -> WarehouseLocationResponse:
        location = await service.create(input)
        return WarehouseLocationResponse.from_orm_model(location)

    @strawberry.mutation
    @inject
    async def update_warehouse_location(
        self,
        id: UUID,
        input: WarehouseLocationInput,
        service: Injected[WarehouseLocationService],
    ) -> WarehouseLocationResponse:
        location = await service.update(id, input)
        return WarehouseLocationResponse.from_orm_model(location)

    @strawberry.mutation
    @inject
    async def delete_warehouse_location(
        self,
        id: UUID,
        service: Injected[WarehouseLocationService],
    ) -> bool:
        """Delete a warehouse location (cascade deletes children)."""
        return await service.delete(id)

    @strawberry.mutation
    @inject
    async def bulk_save_warehouse_locations(
        self,
        warehouse_id: UUID,
        locations: list[BulkWarehouseLocationInput],
        service: Injected[WarehouseLocationBulkService],
    ) -> list[WarehouseLocationResponse]:
        """Bulk save warehouse locations.

        Creates new locations, updates existing ones, and deletes
        any existing locations not in the input.
        """
        saved = await service.bulk_save(warehouse_id, locations)
        return WarehouseLocationResponse.from_orm_model_list(saved)

    @strawberry.mutation
    @inject
    async def assign_product_to_location(
        self,
        location_id: UUID,
        product_id: UUID,
        quantity: Decimal,
        service: Injected[WarehouseLocationAssignmentService],
    ) -> LocationProductAssignmentResponse:
        assignment = await service.assign_product(location_id, product_id, quantity)
        return LocationProductAssignmentResponse.from_orm_model(assignment)

    @strawberry.mutation
    @inject
    async def update_product_quantity_at_location(
        self,
        location_id: UUID,
        product_id: UUID,
        quantity: Decimal,
        service: Injected[WarehouseLocationAssignmentService],
    ) -> LocationProductAssignmentResponse:
        assignment = await service.update_product_quantity(
            location_id, product_id, quantity
        )
        return LocationProductAssignmentResponse.from_orm_model(assignment)

    @strawberry.mutation
    @inject
    async def remove_product_from_location(
        self,
        location_id: UUID,
        product_id: UUID,
        service: Injected[WarehouseLocationAssignmentService],
    ) -> bool:
        return await service.remove_product(location_id, product_id)

    @strawberry.mutation
    @inject
    async def bulk_assign_products_to_locations(
        self,
        assignments: list[BulkProductAssignmentInput],
        service: Injected[WarehouseLocationAssignmentService],
    ) -> list[LocationProductAssignmentResponse]:
        """Bulk assign products to locations in a single request.

        More efficient than calling assignProductToLocation multiple times.
        Creates new assignments or updates existing ones.
        """
        tuples = [(a.location_id, a.product_id, a.quantity) for a in assignments]
        results = await service.bulk_assign_products(tuples)
        return LocationProductAssignmentResponse.from_orm_model_list(results)

    @strawberry.mutation
    @inject
    async def bulk_remove_products_from_locations(
        self,
        removals: list[BulkProductRemovalInput],
        service: Injected[WarehouseLocationAssignmentService],
    ) -> int:
        """Bulk remove products from locations in a single request.

        More efficient than calling removeProductFromLocation multiple times.
        Returns the number of assignments successfully removed.
        """
        tuples = [(r.location_id, r.product_id) for r in removals]
        return await service.bulk_remove_products(tuples)
