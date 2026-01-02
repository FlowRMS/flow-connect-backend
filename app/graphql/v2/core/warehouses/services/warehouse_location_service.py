"""Service layer for warehouse location operations."""

from decimal import Decimal
from uuid import UUID

from commons.db.v6 import (
    LocationProductAssignment,
    WarehouseLocation,
    WarehouseStructureCode,
)

from app.errors.common_errors import NotFoundError, ValidationError
from app.graphql.v2.core.warehouses.repositories import (
    LocationProductAssignmentRepository,
    WarehouseLocationRepository,
    WarehouseRepository,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_location_input import (
    BulkWarehouseLocationInput,
    WarehouseLocationInput,
)

# Level hierarchy - each level can only have a parent of the previous level
LEVEL_HIERARCHY = {
    WarehouseStructureCode.SECTION: None,  # Sections have no parent
    WarehouseStructureCode.AISLE: WarehouseStructureCode.SECTION,
    WarehouseStructureCode.SHELF: WarehouseStructureCode.AISLE,
    WarehouseStructureCode.BAY: WarehouseStructureCode.SHELF,
    WarehouseStructureCode.ROW: WarehouseStructureCode.BAY,
    WarehouseStructureCode.BIN: WarehouseStructureCode.ROW,
}


class WarehouseLocationService:
    """Service for warehouse location operations."""

    def __init__(
        self,
        location_repository: WarehouseLocationRepository,
        assignment_repository: LocationProductAssignmentRepository,
        warehouse_repository: WarehouseRepository,
    ) -> None:
        super().__init__()
        self.location_repository = location_repository
        self.assignment_repository = assignment_repository
        self.warehouse_repository = warehouse_repository

    # Location CRUD
    async def get_by_id(self, location_id: UUID) -> WarehouseLocation:
        """Get a location by ID."""
        location = await self.location_repository.get_by_id_with_children(location_id)
        if not location:
            raise NotFoundError(f"Location with id {location_id} not found")
        return location

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[WarehouseLocation]:
        """Get all locations for a warehouse (flat list)."""
        # Verify warehouse exists
        if not await self.warehouse_repository.exists(warehouse_id):
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")
        return await self.location_repository.list_by_warehouse(warehouse_id)

    async def get_location_tree(self, warehouse_id: UUID) -> list[WarehouseLocation]:
        """Get location tree for a warehouse (root locations with children loaded)."""
        # Verify warehouse exists
        if not await self.warehouse_repository.exists(warehouse_id):
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")
        return await self.location_repository.get_root_locations(warehouse_id)

    async def create(self, input: WarehouseLocationInput) -> WarehouseLocation:
        """Create a new location."""
        # Verify warehouse exists
        if not await self.warehouse_repository.exists(input.warehouse_id):
            raise NotFoundError(f"Warehouse with id {input.warehouse_id} not found")

        # Validate parent-child hierarchy
        await self._validate_hierarchy(
            WarehouseStructureCode(input.level.value), input.parent_id
        )

        location = WarehouseLocation(
            warehouse_id=input.warehouse_id,
            parent_id=input.parent_id,
            level=WarehouseStructureCode(input.level.value),
            name=input.name,
            code=input.code,
            description=input.description,
            is_active=input.is_active if input.is_active is not None else True,
            sort_order=input.sort_order if input.sort_order is not None else 0,
            x=Decimal(str(input.x)) if input.x is not None else None,
            y=Decimal(str(input.y)) if input.y is not None else None,
            width=Decimal(str(input.width)) if input.width is not None else None,
            height=Decimal(str(input.height)) if input.height is not None else None,
            rotation=Decimal(str(input.rotation))
            if input.rotation is not None
            else None,
        )
        return await self.location_repository.create(location)

    async def update(
        self, location_id: UUID, input: WarehouseLocationInput
    ) -> WarehouseLocation:
        """Update a location."""
        existing = await self.location_repository.get_by_id(location_id)
        if not existing:
            raise NotFoundError(f"Location with id {location_id} not found")

        # Validate parent-child hierarchy if changing parent
        if input.parent_id != existing.parent_id:
            await self._validate_hierarchy(
                WarehouseStructureCode(input.level.value), input.parent_id
            )

        # Update fields
        location = WarehouseLocation(
            warehouse_id=input.warehouse_id,
            parent_id=input.parent_id,
            level=WarehouseStructureCode(input.level.value),
            name=input.name,
            code=input.code,
            description=input.description,
            is_active=input.is_active if input.is_active is not None else True,
            sort_order=input.sort_order if input.sort_order is not None else 0,
            x=Decimal(str(input.x)) if input.x is not None else None,
            y=Decimal(str(input.y)) if input.y is not None else None,
            width=Decimal(str(input.width)) if input.width is not None else None,
            height=Decimal(str(input.height)) if input.height is not None else None,
            rotation=Decimal(str(input.rotation))
            if input.rotation is not None
            else None,
        )
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

        This handles creates, updates, and implicit deletes.
        Locations not in the input but existing in DB will be deleted.

        Supports temp_id and temp_parent_id for newly created hierarchical locations:
        - temp_id: A temporary ID for new locations (e.g., "SECTION-123456789")
        - temp_parent_id: Reference to a temp_id of a parent that's also being created
        """
        # Verify warehouse exists
        if not await self.warehouse_repository.exists(warehouse_id):
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")

        # Get existing locations
        existing_locations = await self.location_repository.list_by_warehouse(
            warehouse_id
        )
        existing_ids = {loc.id for loc in existing_locations}

        # Track which IDs are in the input
        input_ids: set[UUID] = set()
        result: list[WarehouseLocation] = []

        # Map temp_id -> real UUID for newly created locations
        temp_id_to_real_id: dict[str, UUID] = {}

        # Separate locations into those with real parent_id and those with temp_parent_id
        locations_with_real_parent: list[BulkWarehouseLocationInput] = []
        locations_with_temp_parent: list[BulkWarehouseLocationInput] = []

        for loc_input in locations:
            if loc_input.temp_parent_id:
                locations_with_temp_parent.append(loc_input)
            else:
                locations_with_real_parent.append(loc_input)

        # Process locations with real parent_id first (including root-level)
        for loc_input in locations_with_real_parent:
            if loc_input.id and loc_input.id in existing_ids:
                # Update existing
                input_ids.add(loc_input.id)
                location = WarehouseLocation(
                    warehouse_id=warehouse_id,
                    parent_id=loc_input.parent_id,
                    level=WarehouseStructureCode(loc_input.level.value),
                    name=loc_input.name,
                    code=loc_input.code,
                    description=loc_input.description,
                    is_active=loc_input.is_active
                    if loc_input.is_active is not None
                    else True,
                    sort_order=loc_input.sort_order
                    if loc_input.sort_order is not None
                    else 0,
                    x=Decimal(str(loc_input.x)) if loc_input.x is not None else None,
                    y=Decimal(str(loc_input.y)) if loc_input.y is not None else None,
                    width=Decimal(str(loc_input.width))
                    if loc_input.width is not None
                    else None,
                    height=Decimal(str(loc_input.height))
                    if loc_input.height is not None
                    else None,
                    rotation=Decimal(str(loc_input.rotation))
                    if loc_input.rotation is not None
                    else None,
                )
                location.id = loc_input.id
                updated = await self.location_repository.update(location)
                result.append(updated)
                # Track temp_id mapping if provided
                if loc_input.temp_id:
                    temp_id_to_real_id[loc_input.temp_id] = updated.id
            else:
                # Create new
                location = WarehouseLocation(
                    warehouse_id=warehouse_id,
                    parent_id=loc_input.parent_id,
                    level=WarehouseStructureCode(loc_input.level.value),
                    name=loc_input.name,
                    code=loc_input.code,
                    description=loc_input.description,
                    is_active=loc_input.is_active
                    if loc_input.is_active is not None
                    else True,
                    sort_order=loc_input.sort_order
                    if loc_input.sort_order is not None
                    else 0,
                    x=Decimal(str(loc_input.x)) if loc_input.x is not None else None,
                    y=Decimal(str(loc_input.y)) if loc_input.y is not None else None,
                    width=Decimal(str(loc_input.width))
                    if loc_input.width is not None
                    else None,
                    height=Decimal(str(loc_input.height))
                    if loc_input.height is not None
                    else None,
                    rotation=Decimal(str(loc_input.rotation))
                    if loc_input.rotation is not None
                    else None,
                )
                created = await self.location_repository.create(location)
                result.append(created)
                # Track temp_id mapping if provided
                if loc_input.temp_id:
                    temp_id_to_real_id[loc_input.temp_id] = created.id

        # Now process locations with temp_parent_id (children of newly created parents)
        for loc_input in locations_with_temp_parent:
            # Resolve temp_parent_id to real UUID
            real_parent_id = (
                temp_id_to_real_id.get(loc_input.temp_parent_id)
                if loc_input.temp_parent_id
                else None
            )
            if not real_parent_id:
                # Parent wasn't found - this shouldn't happen if frontend sends data correctly
                # Fall back to null parent
                real_parent_id = None

            if loc_input.id and loc_input.id in existing_ids:
                # Update existing
                input_ids.add(loc_input.id)
                location = WarehouseLocation(
                    warehouse_id=warehouse_id,
                    parent_id=real_parent_id,
                    level=WarehouseStructureCode(loc_input.level.value),
                    name=loc_input.name,
                    code=loc_input.code,
                    description=loc_input.description,
                    is_active=loc_input.is_active
                    if loc_input.is_active is not None
                    else True,
                    sort_order=loc_input.sort_order
                    if loc_input.sort_order is not None
                    else 0,
                    x=Decimal(str(loc_input.x)) if loc_input.x is not None else None,
                    y=Decimal(str(loc_input.y)) if loc_input.y is not None else None,
                    width=Decimal(str(loc_input.width))
                    if loc_input.width is not None
                    else None,
                    height=Decimal(str(loc_input.height))
                    if loc_input.height is not None
                    else None,
                    rotation=Decimal(str(loc_input.rotation))
                    if loc_input.rotation is not None
                    else None,
                )
                location.id = loc_input.id
                updated = await self.location_repository.update(location)
                result.append(updated)
                if loc_input.temp_id:
                    temp_id_to_real_id[loc_input.temp_id] = updated.id
            else:
                # Create new
                location = WarehouseLocation(
                    warehouse_id=warehouse_id,
                    parent_id=real_parent_id,
                    level=WarehouseStructureCode(loc_input.level.value),
                    name=loc_input.name,
                    code=loc_input.code,
                    description=loc_input.description,
                    is_active=loc_input.is_active
                    if loc_input.is_active is not None
                    else True,
                    sort_order=loc_input.sort_order
                    if loc_input.sort_order is not None
                    else 0,
                    x=Decimal(str(loc_input.x)) if loc_input.x is not None else None,
                    y=Decimal(str(loc_input.y)) if loc_input.y is not None else None,
                    width=Decimal(str(loc_input.width))
                    if loc_input.width is not None
                    else None,
                    height=Decimal(str(loc_input.height))
                    if loc_input.height is not None
                    else None,
                    rotation=Decimal(str(loc_input.rotation))
                    if loc_input.rotation is not None
                    else None,
                )
                created = await self.location_repository.create(location)
                result.append(created)
                if loc_input.temp_id:
                    temp_id_to_real_id[loc_input.temp_id] = created.id

        # Delete locations that were removed from input
        ids_to_delete = existing_ids - input_ids
        for location_id in ids_to_delete:
            _ = await self.location_repository.delete(location_id)

        return result

    async def _validate_hierarchy(
        self,
        level: WarehouseStructureCode,
        parent_id: UUID | None,
    ) -> None:
        """Validate that the parent-child hierarchy is correct."""
        expected_parent_level = LEVEL_HIERARCHY.get(level)

        if expected_parent_level is None:
            # This is a section - should have no parent
            if parent_id is not None:
                raise ValidationError(
                    f"Sections cannot have a parent. Got parent_id={parent_id}"
                )
        else:
            # Non-section levels must have a parent
            if parent_id is None:
                raise ValidationError(
                    f"{level.name} locations must have a parent of type "
                    f"{expected_parent_level.name}"
                )

            # Verify parent exists and is correct level
            parent = await self.location_repository.get_by_id(parent_id)
            if not parent:
                raise NotFoundError(f"Parent location with id {parent_id} not found")

            if parent.level != expected_parent_level:
                raise ValidationError(
                    f"{level.name} locations must have a parent of type "
                    f"{expected_parent_level.name}, but got {parent.level.name}"
                )

    # Product assignment operations
    async def assign_product(
        self, location_id: UUID, product_id: UUID, quantity: int
    ) -> LocationProductAssignment:
        """Assign a product to a location."""
        # Verify location exists
        location = await self.location_repository.get_by_id(location_id)
        if not location:
            raise NotFoundError(f"Location with id {location_id} not found")

        # Check for existing assignment
        existing = await self.assignment_repository.get_by_location_and_product(
            location_id, product_id
        )
        if existing:
            # Update quantity
            existing.quantity = quantity
            return await self.assignment_repository.update(existing)

        # Create new assignment
        assignment = LocationProductAssignment(
            location_id=location_id,
            product_id=product_id,
            quantity=quantity,
        )
        return await self.assignment_repository.create(assignment)

    async def update_product_quantity(
        self, location_id: UUID, product_id: UUID, quantity: int
    ) -> LocationProductAssignment:
        """Update product quantity at a location."""
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
        """Remove a product from a location."""
        return await self.assignment_repository.delete_by_location_and_product(
            location_id, product_id
        )

    async def get_assignments_by_location(
        self, location_id: UUID
    ) -> list[LocationProductAssignment]:
        """Get all product assignments for a location."""
        return await self.assignment_repository.list_by_location(location_id)

    async def get_assignments_by_product(
        self, product_id: UUID
    ) -> list[LocationProductAssignment]:
        """Get all location assignments for a product."""
        return await self.assignment_repository.list_by_product(product_id)
