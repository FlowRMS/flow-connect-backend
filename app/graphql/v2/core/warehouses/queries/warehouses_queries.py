from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.v2.core.warehouses.services.warehouse_service import WarehouseService
from app.graphql.v2.core.warehouses.strawberry.warehouse_response import (
    WarehouseMemberResponse,
    WarehouseResponse,
    WarehouseSettingsResponse,
    WarehouseStructureResponse,
)


@strawberry.type
class WarehousesQueries:
    """GraphQL queries for Warehouse entity."""

    @strawberry.field
    @inject
    async def warehouses(
        self,
        service: Injected[WarehouseService],
    ) -> list[WarehouseResponse]:
        """Get all warehouses."""
        warehouses = await service.list_all()
        return WarehouseResponse.from_orm_model_list(warehouses)

    @strawberry.field
    @inject
    async def warehouse(
        self,
        id: UUID,
        service: Injected[WarehouseService],
    ) -> WarehouseResponse:
        """Get a warehouse by ID."""
        warehouse = await service.get_by_id(id)
        return WarehouseResponse.from_orm_model(warehouse)

    @strawberry.field
    @inject
    async def warehouse_members(
        self,
        warehouse_id: UUID,
        service: Injected[WarehouseService],
    ) -> list[WarehouseMemberResponse]:
        """Get all members for a warehouse."""
        members = await service.get_members(warehouse_id)
        return WarehouseMemberResponse.from_orm_model_list(members)

    @strawberry.field
    @inject
    async def warehouse_settings(
        self,
        warehouse_id: UUID,
        service: Injected[WarehouseService],
    ) -> WarehouseSettingsResponse | None:
        """Get settings for a warehouse."""
        settings = await service.get_settings(warehouse_id)
        return WarehouseSettingsResponse.from_orm_model_optional(settings)

    @strawberry.field
    @inject
    async def warehouse_structure(
        self,
        warehouse_id: UUID,
        service: Injected[WarehouseService],
    ) -> list[WarehouseStructureResponse]:
        """Get location level configuration for a warehouse."""
        structure = await service.get_structure(warehouse_id)
        return WarehouseStructureResponse.from_orm_model_list(structure)
