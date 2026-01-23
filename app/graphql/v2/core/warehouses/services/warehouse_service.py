"""Service layer for warehouse operations."""

from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6 import (
    Warehouse,
    WarehouseMember,
    WarehouseMemberRole,
    WarehouseSettings,
    WarehouseStructure,
)

from app.errors.common_errors import NotFoundError
from app.graphql.v2.core.warehouses.repositories import (
    WarehouseMembersRepository,
    WarehouseRepository,
    WarehouseSettingsRepository,
    WarehouseStructureRepository,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_input import (
    WarehouseInput,
    WarehouseSettingsInput,
    WarehouseStructureLevelInput,
)


class WarehouseService:
    """Service for warehouse operations."""

    def __init__(
        self,
        repository: WarehouseRepository,
        members_repository: WarehouseMembersRepository,
        settings_repository: WarehouseSettingsRepository,
        structure_repository: WarehouseStructureRepository,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.members_repository = members_repository
        self.settings_repository = settings_repository
        self.structure_repository = structure_repository
        self.auth_info = auth_info

    # Warehouse CRUD
    async def get_by_id(self, warehouse_id: UUID) -> Warehouse:
        """Get a warehouse by ID."""
        warehouse = await self.repository.get_with_relations(warehouse_id)
        if not warehouse:
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")
        return warehouse

    async def list_all(self) -> list[Warehouse]:
        """Get all warehouses."""
        return await self.repository.list_all_with_relations()

    async def create(self, input: WarehouseInput) -> Warehouse:
        """Create a new warehouse."""
        return await self.repository.create(input.to_orm_model())

    async def update(self, warehouse_id: UUID, input: WarehouseInput) -> Warehouse:
        """Update a warehouse using base repository update."""
        if not await self.repository.exists(warehouse_id):
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")

        # Create model from input and set the ID
        warehouse = input.to_orm_model()
        warehouse.id = warehouse_id
        return await self.repository.update(warehouse)

    async def delete(self, warehouse_id: UUID) -> bool:
        """Soft-delete a warehouse by setting is_active = False."""
        warehouse = await self.repository.soft_delete(warehouse_id)
        if not warehouse:
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")
        return True

    # Worker management
    async def assign_worker(
        self, warehouse_id: UUID, user_id: UUID, role: WarehouseMemberRole
    ) -> WarehouseMember:
        """Assign a worker to a warehouse."""
        # Check if already assigned
        existing = await self.members_repository.get_by_warehouse_and_user(
            warehouse_id, user_id
        )
        if existing:
            # Update role using repository update
            existing.role = role
            return await self.members_repository.update(existing)

        # Create new assignment
        member = WarehouseMember(
            warehouse_id=warehouse_id,
            user_id=user_id,
            role=role,
        )
        return await self.members_repository.create(member)

    async def update_worker_role(
        self, warehouse_id: UUID, user_id: UUID, role: WarehouseMemberRole
    ) -> WarehouseMember:
        """Update a worker's role."""
        member = await self.members_repository.get_by_warehouse_and_user(
            warehouse_id, user_id
        )
        if not member:
            raise NotFoundError(
                f"Worker {user_id} not found in warehouse {warehouse_id}"
            )
        member.role = role
        return await self.members_repository.update(member)

    async def remove_worker(self, warehouse_id: UUID, user_id: UUID) -> bool:
        """Remove a worker from a warehouse."""
        member = await self.members_repository.get_by_warehouse_and_user(
            warehouse_id, user_id
        )
        if not member:
            raise NotFoundError(
                f"Worker {user_id} not found in warehouse {warehouse_id}"
            )
        return await self.members_repository.delete(member.id)

    async def get_members(self, warehouse_id: UUID) -> list[WarehouseMember]:
        """Get all members for a warehouse."""
        return await self.members_repository.list_by_warehouse(warehouse_id)

    # Settings management
    async def get_settings(self, warehouse_id: UUID) -> WarehouseSettings | None:
        """Get settings for a warehouse."""
        return await self.settings_repository.get_by_warehouse(warehouse_id)

    async def update_settings(self, input: WarehouseSettingsInput) -> WarehouseSettings:
        """Update or create warehouse settings."""
        existing = await self.settings_repository.get_by_warehouse(input.warehouse_id)
        if existing:
            # Use repository update pattern
            settings = input.to_orm_model()
            settings.id = existing.id
            return await self.settings_repository.update(settings)
        return await self.settings_repository.create(input.to_orm_model())

    # Structure (location level configuration) management
    async def get_structure(self, warehouse_id: UUID) -> list[WarehouseStructure]:
        """Get location level configuration for a warehouse."""
        return await self.structure_repository.list_by_warehouse(warehouse_id)

    async def update_structure(
        self, warehouse_id: UUID, levels: list[WarehouseStructureLevelInput]
    ) -> list[WarehouseStructure]:
        """Update location level configuration for a warehouse.

        This replaces all existing structure entries.
        """
        # Delete existing structure
        await self.structure_repository.delete_by_warehouse(warehouse_id)

        # Create new structure entries
        result = []
        for level in levels:
            structure = WarehouseStructure(
                warehouse_id=warehouse_id,
                code=level.code,
                level_order=level.level_order,
            )
            created = await self.structure_repository.create(structure)
            result.append(created)

        return result
