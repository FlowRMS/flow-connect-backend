from decimal import Decimal
from uuid import UUID

from commons.db.v6 import WarehouseLocation, WarehouseStructureCode

from app.errors.common_errors import NotFoundError, ValidationError
from app.graphql.v2.core.warehouses.repositories import (
    WarehouseLocationRepository,
    WarehouseRepository,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_location_input import (
    BulkWarehouseLocationInput,
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
        await self._validate_hierarchy(
            WarehouseStructureCode(input.level.value), input.parent_id
        )
        location = self._build_location(input, input.warehouse_id, input.parent_id)
        return await self.location_repository.create(location)

    async def update(
        self, location_id: UUID, input: WarehouseLocationInput
    ) -> WarehouseLocation:
        existing = await self.location_repository.get_by_id(location_id)
        if not existing:
            raise NotFoundError(f"Location with id {location_id} not found")
        if input.parent_id != existing.parent_id:
            await self._validate_hierarchy(
                WarehouseStructureCode(input.level.value), input.parent_id
            )
        location = self._build_location(input, input.warehouse_id, input.parent_id)
        location.id = location_id
        return await self.location_repository.update(location)

    async def delete(self, location_id: UUID) -> bool:
        """Delete a location (cascade deletes children)."""
        if not await self.location_repository.exists(location_id):
            raise NotFoundError(f"Location with id {location_id} not found")
        return await self.location_repository.delete(location_id)

    async def bulk_save(
        self, warehouse_id: UUID, locations: list[BulkWarehouseLocationInput]
    ) -> list[WarehouseLocation]:
        """Bulk save locations for a warehouse.

        Handles creates, updates, and implicit deletes. Locations not in input are deleted.
        Supports temp_id/temp_parent_id for newly created hierarchical locations.
        """
        if not await self.warehouse_repository.exists(warehouse_id):
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")

        existing = await self.location_repository.list_by_warehouse(warehouse_id)
        existing_ids = {loc.id for loc in existing}
        input_ids: set[UUID] = set()
        result: list[WarehouseLocation] = []
        temp_id_map: dict[str, UUID] = {}

        with_real_parent = [loc for loc in locations if not loc.temp_parent_id]
        with_temp_parent = [loc for loc in locations if loc.temp_parent_id]

        for loc in with_real_parent:
            saved = await self._save_location(
                loc, warehouse_id, loc.parent_id, existing_ids, input_ids, temp_id_map
            )
            result.append(saved)

        for loc in with_temp_parent:
            parent_id = temp_id_map.get(loc.temp_parent_id) if loc.temp_parent_id else None
            saved = await self._save_location(
                loc, warehouse_id, parent_id, existing_ids, input_ids, temp_id_map
            )
            result.append(saved)

        for loc_id in existing_ids - input_ids:
            _ = await self.location_repository.delete(loc_id)

        return result

    async def _save_location(
        self,
        loc: BulkWarehouseLocationInput,
        warehouse_id: UUID,
        parent_id: UUID | None,
        existing_ids: set[UUID],
        input_ids: set[UUID],
        temp_id_map: dict[str, UUID],
    ) -> WarehouseLocation:
        location = self._build_location(loc, warehouse_id, parent_id)
        if loc.id and loc.id in existing_ids:
            input_ids.add(loc.id)
            location.id = loc.id
            saved = await self.location_repository.update(location)
        else:
            saved = await self.location_repository.create(location)
        if loc.temp_id:
            temp_id_map[loc.temp_id] = saved.id
        return saved

    def _build_location(
        self,
        inp: WarehouseLocationInput | BulkWarehouseLocationInput,
        warehouse_id: UUID,
        parent_id: UUID | None,
    ) -> WarehouseLocation:
        return WarehouseLocation(
            warehouse_id=warehouse_id,
            parent_id=parent_id,
            level=WarehouseStructureCode(inp.level.value),
            name=inp.name,
            code=inp.code,
            description=inp.description,
            is_active=inp.is_active if inp.is_active is not None else True,
            sort_order=inp.sort_order if inp.sort_order is not None else 0,
            x=Decimal(str(inp.x)) if inp.x is not None else None,
            y=Decimal(str(inp.y)) if inp.y is not None else None,
            width=Decimal(str(inp.width)) if inp.width is not None else None,
            height=Decimal(str(inp.height)) if inp.height is not None else None,
            rotation=Decimal(str(inp.rotation)) if inp.rotation is not None else None,
        )

    async def _validate_hierarchy(
        self, level: WarehouseStructureCode, parent_id: UUID | None
    ) -> None:
        expected_parent = LEVEL_HIERARCHY.get(level)
        if expected_parent is None:
            if parent_id is not None:
                raise ValidationError(f"Sections cannot have a parent. Got parent_id={parent_id}")
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
