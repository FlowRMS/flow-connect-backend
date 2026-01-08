from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.warehouses.services.warehouse_location_service import (
    WarehouseLocationService,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_location_response import (
    LocationProductAssignmentResponse,
    WarehouseLocationResponse,
)


@strawberry.type
class WarehouseLocationQueries:
    @strawberry.field
    @inject
    async def warehouse_locations(
        self,
        warehouse_id: UUID,
        service: Injected[WarehouseLocationService],
    ) -> list[WarehouseLocationResponse]:
        """Get all locations for a warehouse (flat list)."""
        locations = await service.list_by_warehouse(warehouse_id)
        return WarehouseLocationResponse.from_orm_model_list(locations)

    @strawberry.field
    @inject
    async def warehouse_location_tree(
        self,
        warehouse_id: UUID,
        service: Injected[WarehouseLocationService],
    ) -> list[WarehouseLocationResponse]:
        """Get location tree for a warehouse (root locations with nested children)."""
        locations = await service.get_location_tree(warehouse_id)
        return WarehouseLocationResponse.from_orm_model_list(locations)

    @strawberry.field
    @inject
    async def warehouse_location(
        self,
        id: UUID,
        service: Injected[WarehouseLocationService],
    ) -> WarehouseLocationResponse:
        location = await service.get_by_id(id)
        return WarehouseLocationResponse.from_orm_model(location)

    @strawberry.field
    @inject
    async def location_product_assignments(
        self,
        location_id: UUID,
        service: Injected[WarehouseLocationService],
    ) -> list[LocationProductAssignmentResponse]:
        assignments = await service.get_assignments_by_location(location_id)
        return LocationProductAssignmentResponse.from_orm_model_list(assignments)

    @strawberry.field
    @inject
    async def product_location_assignments(
        self,
        product_id: UUID,
        service: Injected[WarehouseLocationService],
    ) -> list[LocationProductAssignmentResponse]:
        assignments = await service.get_assignments_by_product(product_id)
        return LocationProductAssignmentResponse.from_orm_model_list(assignments)
