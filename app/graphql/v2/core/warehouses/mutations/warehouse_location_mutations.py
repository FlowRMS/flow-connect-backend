"""GraphQL mutations for warehouse locations."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.warehouses.services.warehouse_location_service import (
    WarehouseLocationService,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_location_input import (
    BulkWarehouseLocationInput,
    WarehouseLocationInput,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_location_response import (
    LocationProductAssignmentResponse,
    WarehouseLocationResponse,
)


@strawberry.type
class WarehouseLocationMutations:
    """GraphQL mutations for WarehouseLocation entity."""

    # Location CRUD
    @strawberry.mutation
    @inject
    async def create_warehouse_location(
        self,
        input: WarehouseLocationInput,
        service: Injected[WarehouseLocationService],
    ) -> WarehouseLocationResponse:
        """Create a new warehouse location."""
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
        """Update a warehouse location."""
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
        service: Injected[WarehouseLocationService],
    ) -> list[WarehouseLocationResponse]:
        """Bulk save warehouse locations.

        Creates new locations, updates existing ones, and deletes
        any existing locations not in the input.
        """
        saved = await service.bulk_save(warehouse_id, locations)
        return WarehouseLocationResponse.from_orm_model_list(saved)

    # Product assignment mutations
    @strawberry.mutation
    @inject
    async def assign_product_to_location(
        self,
        location_id: UUID,
        product_id: UUID,
        quantity: int,
        service: Injected[WarehouseLocationService],
    ) -> LocationProductAssignmentResponse:
        """Assign a product to a location."""
        assignment = await service.assign_product(location_id, product_id, quantity)
        return LocationProductAssignmentResponse.from_orm_model(assignment)

    @strawberry.mutation
    @inject
    async def update_product_quantity_at_location(
        self,
        location_id: UUID,
        product_id: UUID,
        quantity: int,
        service: Injected[WarehouseLocationService],
    ) -> LocationProductAssignmentResponse:
        """Update product quantity at a location."""
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
        service: Injected[WarehouseLocationService],
    ) -> bool:
        """Remove a product from a location."""
        return await service.remove_product(location_id, product_id)
