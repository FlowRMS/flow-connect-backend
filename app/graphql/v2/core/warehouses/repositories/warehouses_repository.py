"""Repository for warehouse operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.core.warehouses.models import (
    Warehouse,
    WarehouseMember,
    WarehouseSettings,
    WarehouseStructure,
)


class WarehousesRepository(BaseRepository[Warehouse]):
    """Repository for Warehouse entity."""

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Warehouse,
        )

    async def get_with_relations(self, warehouse_id: UUID) -> Warehouse | None:
        """Get warehouse with all related data (members, settings, structure)."""
        stmt = (
            select(Warehouse)
            .options(
                selectinload(Warehouse.members),
                selectinload(Warehouse.settings),
                selectinload(Warehouse.structure),
            )
            .where(Warehouse.id == warehouse_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all_with_relations(self) -> list[Warehouse]:
        """Get all warehouses with related data."""
        stmt = select(Warehouse).options(
            selectinload(Warehouse.members),
            selectinload(Warehouse.settings),
            selectinload(Warehouse.structure),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class WarehouseMembersRepository(BaseRepository[WarehouseMember]):
    """Repository for WarehouseMember entity."""

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            WarehouseMember,
        )

    async def get_by_warehouse_and_user(
        self, warehouse_id: UUID, user_id: UUID
    ) -> WarehouseMember | None:
        """Get a member by warehouse and user IDs."""
        stmt = select(WarehouseMember).where(
            WarehouseMember.warehouse_id == warehouse_id,
            WarehouseMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[WarehouseMember]:
        """Get all members for a warehouse."""
        stmt = select(WarehouseMember).where(
            WarehouseMember.warehouse_id == warehouse_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class WarehouseSettingsRepository(BaseRepository[WarehouseSettings]):
    """Repository for WarehouseSettings entity."""

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            WarehouseSettings,
        )

    async def get_by_warehouse(self, warehouse_id: UUID) -> WarehouseSettings | None:
        """Get settings for a warehouse."""
        stmt = select(WarehouseSettings).where(
            WarehouseSettings.warehouse_id == warehouse_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


class WarehouseStructureRepository(BaseRepository[WarehouseStructure]):
    """Repository for WarehouseStructure entity (location level configuration)."""

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            WarehouseStructure,
        )

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[WarehouseStructure]:
        """Get all structure levels for a warehouse, ordered by level_order."""
        stmt = (
            select(WarehouseStructure)
            .where(WarehouseStructure.warehouse_id == warehouse_id)
            .order_by(WarehouseStructure.level_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_warehouse(self, warehouse_id: UUID) -> None:
        """Delete all structure entries for a warehouse."""
        stmt = select(WarehouseStructure).where(
            WarehouseStructure.warehouse_id == warehouse_id
        )
        result = await self.session.execute(stmt)
        for item in result.scalars().all():
            await self.session.delete(item)
        await self.session.flush()
