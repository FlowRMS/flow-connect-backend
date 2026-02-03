import logging
from decimal import Decimal
from uuid import UUID

from commons.db.v6 import WarehouseLocation
from commons.db.v6.warehouse.inventory.inventory_item import InventoryItem
from sqlalchemy import select

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.warehouses.repositories import (
    WarehouseLocationRepository,
    WarehouseRepository,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_location_input import (
    BulkWarehouseLocationInput,
)


class WarehouseLocationBulkService:
    """Service for bulk warehouse location operations."""

    def __init__(
        self,
        location_repository: WarehouseLocationRepository,
        warehouse_repository: WarehouseRepository,
    ) -> None:
        super().__init__()
        self.location_repository = location_repository
        self.warehouse_repository = warehouse_repository

    async def bulk_save(
        self, warehouse_id: UUID, locations: list[BulkWarehouseLocationInput]
    ) -> list[WarehouseLocation]:
        """Bulk save locations for a warehouse.

        Handles creates, updates, and implicit deletes. Locations not in input are deleted.
        Supports temp_id/temp_parent_id for newly created hierarchical locations.
        """
        logger = logging.getLogger(__name__)

        if not await self.warehouse_repository.exists(warehouse_id):
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")

        existing = await self.location_repository.list_by_warehouse(warehouse_id)
        existing_by_id = {loc.id: loc for loc in existing}
        existing_ids = set(existing_by_id.keys())
        input_ids: set[UUID] = set()
        result: list[WarehouseLocation] = []
        temp_id_map: dict[str, UUID] = {}

        # Debug logging
        logger.info(f"Bulk save: warehouse_id = {warehouse_id}")
        logger.info(f"Bulk save: existing_ids count = {len(existing_ids)}")
        logger.info(f"Bulk save: existing_ids = {list(existing_ids)[:10]}...")
        logger.info(f"Bulk save: input locations count = {len(locations)}")
        input_location_ids = {loc.id for loc in locations if loc.id}
        logger.info(
            f"Bulk save: input location IDs with real IDs = {len(input_location_ids)}"
        )
        logger.info(
            f"Bulk save: input_location_ids = {list(input_location_ids)[:10]}..."
        )

        # Check for IDs that frontend thinks exist but backend doesn't have
        ids_frontend_has_but_backend_doesnt = input_location_ids - existing_ids
        if ids_frontend_has_but_backend_doesnt:
            logger.warning(
                f"Bulk save: Frontend has {len(ids_frontend_has_but_backend_doesnt)} IDs "
                f"not found in backend: {list(ids_frontend_has_but_backend_doesnt)[:5]}..."
            )

        missing_from_input = existing_ids - input_location_ids
        logger.info(
            f"Bulk save: locations that would be deleted = {len(missing_from_input)}"
        )
        if missing_from_input:
            missing_names = [
                loc.name for loc in existing if loc.id in missing_from_input
            ]
            logger.warning(f"Bulk save: locations to delete: {missing_names[:10]}...")

        with_real_parent = [loc for loc in locations if not loc.temp_parent_id]
        with_temp_parent = [loc for loc in locations if loc.temp_parent_id]

        # Sort locations with temp parents to ensure parents are processed
        # before their children
        with_temp_parent = self._topological_sort_by_temp_parent(with_temp_parent)

        for loc in with_real_parent:
            saved = await self._save_location(
                loc, warehouse_id, loc.parent_id, existing_by_id, input_ids, temp_id_map
            )
            result.append(saved)

        for loc in with_temp_parent:
            parent_id = (
                temp_id_map.get(loc.temp_parent_id) if loc.temp_parent_id else None
            )
            if loc.temp_parent_id and parent_id is None:
                logger.warning(
                    f"Could not resolve temp_parent_id '{loc.temp_parent_id}' "
                    f"for location '{loc.name}'. Available temp_ids: {list(temp_id_map.keys())}"
                )
            saved = await self._save_location(
                loc, warehouse_id, parent_id, existing_by_id, input_ids, temp_id_map
            )
            result.append(saved)

        await self.location_repository.session.flush()

        locations_not_in_input = existing_ids - input_ids
        if locations_not_in_input:
            logger.info(
                f"Bulk save: {len(locations_not_in_input)} existing locations not in input "
                f"(will NOT be deleted - use explicit delete if needed)"
            )

        return result

    async def _get_all_descendant_ids(self, location_ids: set[UUID]) -> set[UUID]:
        """Get all descendant location IDs (children, grandchildren, etc.)."""
        all_ids = set(location_ids)
        to_check = list(location_ids)

        while to_check:
            current_id = to_check.pop()
            stmt = select(WarehouseLocation.id).where(
                WarehouseLocation.parent_id == current_id
            )
            result = await self.location_repository.session.execute(stmt)
            child_ids = {row[0] for row in result.fetchall()}
            new_ids = child_ids - all_ids
            all_ids.update(new_ids)
            to_check.extend(new_ids)

        return all_ids

    async def get_locations_with_inventory(self, location_ids: set[UUID]) -> set[UUID]:
        """Check which locations (or their descendants) have inventory items."""
        if not location_ids:
            return set()

        all_affected_ids = await self._get_all_descendant_ids(location_ids)

        stmt = (
            select(InventoryItem.location_id)
            .where(InventoryItem.location_id.in_(all_affected_ids))
            .distinct()
        )
        result = await self.location_repository.session.execute(stmt)
        locations_with_items = {row[0] for row in result.fetchall()}

        affected_top_level: set[UUID] = set()
        for loc_id in location_ids:
            descendants = await self._get_all_descendant_ids({loc_id})
            if descendants & locations_with_items:
                affected_top_level.add(loc_id)

        return affected_top_level

    def _topological_sort_by_temp_parent(
        self, locations: list[BulkWarehouseLocationInput]
    ) -> list[BulkWarehouseLocationInput]:
        """Sort locations so parents are always processed before children."""
        if not locations:
            return locations

        temp_id_to_loc: dict[str, BulkWarehouseLocationInput] = {}
        for loc in locations:
            if loc.temp_id:
                temp_id_to_loc[loc.temp_id] = loc

        visited: set[str] = set()
        result: list[BulkWarehouseLocationInput] = []

        def get_key(loc: BulkWarehouseLocationInput) -> str:
            return loc.temp_id or str(loc.id) or str(id(loc))

        def visit(loc: BulkWarehouseLocationInput) -> None:
            key = get_key(loc)
            if key in visited:
                return
            visited.add(key)

            if loc.temp_parent_id and loc.temp_parent_id in temp_id_to_loc:
                visit(temp_id_to_loc[loc.temp_parent_id])

            result.append(loc)

        for loc in locations:
            visit(loc)

        return result

    async def _save_location(
        self,
        loc: BulkWarehouseLocationInput,
        warehouse_id: UUID,
        parent_id: UUID | None,
        existing_by_id: dict[UUID, WarehouseLocation],
        input_ids: set[UUID],
        temp_id_map: dict[str, UUID],
    ) -> WarehouseLocation:
        logger = logging.getLogger(__name__)
        if loc.id and loc.id in existing_by_id:
            input_ids.add(loc.id)
            try:
                existing = existing_by_id[loc.id]
                existing.warehouse_id = warehouse_id
                existing.parent_id = parent_id
                existing.level = loc.level
                existing.name = loc.name
                existing.code = loc.code
                existing.description = loc.description
                existing.is_active = (
                    loc.is_active if loc.is_active is not None else True
                )
                existing.sort_order = (
                    loc.sort_order if loc.sort_order is not None else 0
                )
                existing.x = Decimal(str(loc.x)) if loc.x is not None else None
                existing.y = Decimal(str(loc.y)) if loc.y is not None else None
                existing.width = (
                    Decimal(str(loc.width)) if loc.width is not None else None
                )
                existing.height = (
                    Decimal(str(loc.height)) if loc.height is not None else None
                )
                existing.rotation = (
                    Decimal(str(loc.rotation)) if loc.rotation is not None else None
                )
                saved = existing
            except Exception as e:
                logger.warning(f"Failed to update location {loc.id}, creating new: {e}")
                new_location = self._build_location(loc, warehouse_id, parent_id)
                saved = await self.location_repository.create(new_location)
        else:
            location = self._build_location(loc, warehouse_id, parent_id)
            saved = await self.location_repository.create(location)
        if loc.temp_id:
            temp_id_map[loc.temp_id] = saved.id
        return saved

    def _build_location(
        self,
        inp: BulkWarehouseLocationInput,
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
            x=Decimal(str(inp.x)) if inp.x is not None else None,
            y=Decimal(str(inp.y)) if inp.y is not None else None,
            width=Decimal(str(inp.width)) if inp.width is not None else None,
            height=Decimal(str(inp.height)) if inp.height is not None else None,
            rotation=Decimal(str(inp.rotation)) if inp.rotation is not None else None,
        )
