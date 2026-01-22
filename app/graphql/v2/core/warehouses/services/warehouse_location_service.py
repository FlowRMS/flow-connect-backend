from uuid import UUID

from commons.db.v6 import WarehouseLocation, WarehouseStructureCode

from app.errors.common_errors import NotFoundError, ValidationError
from app.graphql.v2.core.warehouses.repositories import (
    WarehouseLocationRepository,
    WarehouseRepository,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_location_input import (
    WarehouseLocationInput,
)

LEVEL_HIERARCHY = {
    WarehouseStructureCode.SECTION: None,
    WarehouseStructureCode.AISLE: WarehouseStructureCode.SECTION,
    WarehouseStructureCode.SHELF: WarehouseStructureCode.AISLE,
    WarehouseStructureCode.BAY: WarehouseStructureCode.SHELF,
    WarehouseStructureCode.ROW: WarehouseStructureCode.BAY,
    WarehouseStructureCode.BIN: WarehouseStructureCode.ROW,
}


class WarehouseLocationService:
    """Service for warehouse location CRUD operations."""

    def __init__(
        self,
        location_repository: WarehouseLocationRepository,
        warehouse_repository: WarehouseRepository,
    ) -> None:
        super().__init__()
        self.location_repository = location_repository
        self.warehouse_repository = warehouse_repository

    async def get_by_id(self, location_id: UUID) -> WarehouseLocation:
        location = await self.location_repository.get_by_id_with_children(location_id)
        if not location:
            raise NotFoundError(f"Location with id {location_id} not found")
        return location

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[WarehouseLocation]:
        if not await self.warehouse_repository.exists(warehouse_id):
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")
        return await self.location_repository.list_by_warehouse(warehouse_id)

    async def get_location_tree(self, warehouse_id: UUID) -> list[WarehouseLocation]:
        if not await self.warehouse_repository.exists(warehouse_id):
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")
        return await self.location_repository.get_root_locations(warehouse_id)

    async def create(self, input: WarehouseLocationInput) -> WarehouseLocation:
        if not await self.warehouse_repository.exists(input.warehouse_id):
            raise NotFoundError(f"Warehouse with id {input.warehouse_id} not found")
        await self._validate_hierarchy(input.level, input.parent_id)
        location = self._build_location(input, input.warehouse_id, input.parent_id)
        return await self.location_repository.create(location)

    async def update(
        self, location_id: UUID, input: WarehouseLocationInput
    ) -> WarehouseLocation:
        existing = await self.location_repository.get_by_id(location_id)
        if not existing:
            raise NotFoundError(f"Location with id {location_id} not found")
        if input.parent_id != existing.parent_id:
            await self._validate_hierarchy(input.level, input.parent_id)

        location = self._build_location(input, input.warehouse_id, input.parent_id)
        location.id = location_id
        return await self.location_repository.update(location)

    async def delete(self, location_id: UUID) -> bool:
        """Delete a location (cascade deletes children)."""
        if not await self.location_repository.exists(location_id):
            raise NotFoundError(f"Location with id {location_id} not found")
        return await self.location_repository.delete(location_id)

    def _build_location(
        self,
        inp: WarehouseLocationInput,
        warehouse_id: UUID,
        parent_id: UUID | None,
    ) -> WarehouseLocation:
        return WarehouseLocation(
            warehouse_id=warehouse_id,
            parent_id=parent_id,
            level=inp.level,
            name=inp.name,
            code=inp.code,
            description=inp.description,
            is_active=inp.is_active if inp.is_active is not None else True,
            sort_order=inp.sort_order if inp.sort_order is not None else 0,
            x=inp.x,
            y=inp.y,
            width=inp.width,
            height=inp.height,
            rotation=inp.rotation,
        )

    async def _validate_hierarchy(
        self, level: WarehouseStructureCode, parent_id: UUID | None
    ) -> None:
        expected_parent = LEVEL_HIERARCHY.get(level)
        if expected_parent is None:
            if parent_id is not None:
                raise ValidationError(
                    f"Sections cannot have a parent. Got parent_id={parent_id}"
                )
        else:
            if parent_id is None:
                raise ValidationError(
                    f"{level.name} locations must have a parent of type {expected_parent.name}"
                )
            parent = await self.location_repository.get_by_id(parent_id)
            if not parent:
                raise NotFoundError(f"Parent location with id {parent_id} not found")
            if parent.level != expected_parent:
                raise ValidationError(
                    f"{level.name} locations must have a parent of type "
                    f"{expected_parent.name}, but got {parent.level.name}"
                )
