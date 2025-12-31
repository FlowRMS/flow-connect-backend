"""GraphQL mutations for warehouses."""

from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6 import WarehouseMemberRole

from app.graphql.inject import inject
from app.graphql.v2.core.warehouses.services.warehouse_service import WarehouseService
from app.graphql.v2.core.warehouses.strawberry.warehouse_input import (
    WarehouseInput,
    WarehouseSettingsInput,
    WarehouseStructureLevelInput,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_response import (
    WarehouseMemberResponse,
    WarehouseResponse,
    WarehouseSettingsResponse,
    WarehouseStructureResponse,
)


@strawberry.type
class WarehousesMutations:
    """GraphQL mutations for Warehouse entity."""

    # Warehouse CRUD
    @strawberry.mutation
    @inject
    async def create_warehouse(
        self,
        input: WarehouseInput,
        service: Injected[WarehouseService],
    ) -> WarehouseResponse:
        """Create a new warehouse."""
        warehouse = await service.create(input)
        return WarehouseResponse.from_orm_model(warehouse)

    @strawberry.mutation
    @inject
    async def update_warehouse(
        self,
        id: UUID,
        input: WarehouseInput,
        service: Injected[WarehouseService],
    ) -> WarehouseResponse:
        """Update a warehouse."""
        warehouse = await service.update(id, input)
        return WarehouseResponse.from_orm_model(warehouse)

    @strawberry.mutation
    @inject
    async def delete_warehouse(
        self,
        id: UUID,
        service: Injected[WarehouseService],
    ) -> bool:
        """Delete a warehouse."""
        return await service.delete(id)

    # Worker management
    @strawberry.mutation
    @inject
    async def assign_worker_to_warehouse(
        self,
        warehouse_id: UUID,
        user_id: UUID,
        role: int,
        service: Injected[WarehouseService],
    ) -> WarehouseMemberResponse:
        """Assign a worker to a warehouse. Role: 1=worker, 2=manager."""
        member = await service.assign_worker(
            warehouse_id, user_id, WarehouseMemberRole(role)
        )
        return WarehouseMemberResponse.from_orm_model(member)

    @strawberry.mutation
    @inject
    async def update_worker_role(
        self,
        warehouse_id: UUID,
        user_id: UUID,
        role: int,
        service: Injected[WarehouseService],
    ) -> WarehouseMemberResponse:
        """Update a worker's role. Role: 1=worker, 2=manager."""
        member = await service.update_worker_role(
            warehouse_id, user_id, WarehouseMemberRole(role)
        )
        return WarehouseMemberResponse.from_orm_model(member)

    @strawberry.mutation
    @inject
    async def remove_worker_from_warehouse(
        self,
        warehouse_id: UUID,
        user_id: UUID,
        service: Injected[WarehouseService],
    ) -> bool:
        """Remove a worker from a warehouse."""
        return await service.remove_worker(warehouse_id, user_id)

    # Settings management
    @strawberry.mutation
    @inject
    async def update_warehouse_settings(
        self,
        input: WarehouseSettingsInput,
        service: Injected[WarehouseService],
    ) -> WarehouseSettingsResponse:
        """Update or create warehouse settings."""
        settings = await service.update_settings(input)
        return WarehouseSettingsResponse.from_orm_model(settings)

    # Structure (location level configuration) management
    @strawberry.mutation
    @inject
    async def update_warehouse_structure(
        self,
        warehouse_id: UUID,
        levels: list[WarehouseStructureLevelInput],
        service: Injected[WarehouseService],
    ) -> list[WarehouseStructureResponse]:
        """Update location level configuration for a warehouse.

        This replaces all existing structure entries with the provided levels.
        """
        structure = await service.update_structure(warehouse_id, levels)
        return WarehouseStructureResponse.from_orm_model_list(structure)
