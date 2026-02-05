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
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_settings_input import (
    WarehouseSettingsInput,
)
from app.graphql.v2.core.warehouses.strawberry.warehouse_structure_level_input import (
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
        warehouse = await self.repository.get_with_relations(warehouse_id)
        if not warehouse:
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")
        return warehouse

    async def list_all(self) -> list[Warehouse]:
        return await self.repository.list_all_with_relations()

    async def create(self, input: WarehouseInput) -> Warehouse:
        return await self.repository.create(input.to_orm_model())

    async def update(self, warehouse_id: UUID, input: WarehouseInput) -> Warehouse:
        # Use get_with_relations to ensure warehouse is not soft-deleted
        existing = await self.repository.get_with_relations(warehouse_id)
        if not existing:
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")

        # Create model from input and set the ID
        warehouse = input.to_orm_model()
        warehouse.id = warehouse_id
        # Preserve is_active from existing warehouse to prevent resurrection
        warehouse.is_active = existing.is_active
        return await self.repository.update(warehouse)

    async def delete(self, warehouse_id: UUID) -> bool:
        """Soft-delete a warehouse by setting is_active = False."""
        warehouse = await self.repository.soft_delete(warehouse_id)
        if not warehouse:
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")
        return True

    async def _ensure_warehouse_active(self, warehouse_id: UUID) -> None:
        """Verify warehouse exists and is not soft-deleted."""
        warehouse = await self.repository.get_with_relations(warehouse_id)
        if not warehouse:
            raise NotFoundError(f"Warehouse with id {warehouse_id} not found")

    # Worker management
    async def assign_worker(
        self, warehouse_id: UUID, user_id: UUID, role: WarehouseMemberRole
    ) -> WarehouseMember:
        """Assign a worker to a warehouse."""
        await self._ensure_warehouse_active(warehouse_id)
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
        await self._ensure_warehouse_active(warehouse_id)
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
        await self._ensure_warehouse_active(warehouse_id)
        member = await self.members_repository.get_by_warehouse_and_user(
            warehouse_id, user_id
        )
        if not member:
            raise NotFoundError(
                f"Worker {user_id} not found in warehouse {warehouse_id}"
            )
        return await self.members_repository.delete(member.id)

    async def get_members(self, warehouse_id: UUID) -> list[WarehouseMember]:
        return await self.members_repository.list_by_warehouse(warehouse_id)

    # Settings management
    async def get_settings(self, warehouse_id: UUID) -> WarehouseSettings | None:
        return await self.settings_repository.get_by_warehouse(warehouse_id)

    async def update_settings(self, input: WarehouseSettingsInput) -> WarehouseSettings:
        await self._ensure_warehouse_active(input.warehouse_id)
        existing = await self.settings_repository.get_by_warehouse(input.warehouse_id)
        if existing:
            # Use repository update pattern
            settings = input.to_orm_model()
            settings.id = existing.id
            return await self.settings_repository.update(settings)
        return await self.settings_repository.create(input.to_orm_model())

    # Structure (location level configuration) management
    async def get_structure(self, warehouse_id: UUID) -> list[WarehouseStructure]:
        return await self.structure_repository.list_by_warehouse(warehouse_id)

    async def update_structure(
        self, warehouse_id: UUID, levels: list[WarehouseStructureLevelInput]
    ) -> list[WarehouseStructure]:
        """Update location level configuration for a warehouse.

        This replaces all existing structure entries.
        """
        await self._ensure_warehouse_active(warehouse_id)
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
