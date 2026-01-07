from uuid import UUID

from commons.db.v6 import LocationProductAssignment, WarehouseLocation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class WarehouseLocationRepository(BaseRepository[WarehouseLocation]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            WarehouseLocation,
        )

    async def get_by_id_with_children(
        self, location_id: UUID
    ) -> WarehouseLocation | None:
        stmt = (
            select(WarehouseLocation)
            .options(
                joinedload(WarehouseLocation.children),
                joinedload(WarehouseLocation.product_assignments),
            )
            .where(WarehouseLocation.id == location_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[WarehouseLocation]:
        stmt = (
            select(WarehouseLocation)
            .where(WarehouseLocation.warehouse_id == warehouse_id)
            .order_by(WarehouseLocation.level, WarehouseLocation.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_warehouse_with_children(
        self, warehouse_id: UUID
    ) -> list[WarehouseLocation]:
        stmt = (
            select(WarehouseLocation)
            .options(
                joinedload(WarehouseLocation.children),
                joinedload(WarehouseLocation.product_assignments).joinedload(
                    LocationProductAssignment.product
                ),
            )
            .where(WarehouseLocation.warehouse_id == warehouse_id)
            .order_by(WarehouseLocation.level, WarehouseLocation.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_root_locations(self, warehouse_id: UUID) -> list[WarehouseLocation]:
        stmt = (
            select(WarehouseLocation)
            .options(
                joinedload(WarehouseLocation.children),
                joinedload(WarehouseLocation.product_assignments),
            )
            .where(
                WarehouseLocation.warehouse_id == warehouse_id,
                WarehouseLocation.parent_id.is_(None),
            )
            .order_by(WarehouseLocation.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_children(self, parent_id: UUID) -> list[WarehouseLocation]:
        stmt = (
            select(WarehouseLocation)
            .options(
                joinedload(WarehouseLocation.children),
                joinedload(WarehouseLocation.product_assignments),
            )
            .where(WarehouseLocation.parent_id == parent_id)
            .order_by(WarehouseLocation.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_warehouse(self, warehouse_id: UUID) -> None:
        stmt = select(WarehouseLocation).where(
            WarehouseLocation.warehouse_id == warehouse_id,
            WarehouseLocation.parent_id.is_(None),
        )
        result = await self.session.execute(stmt)
        for item in result.scalars().all():
            await self.session.delete(item)
        await self.session.flush()


class LocationProductAssignmentRepository(BaseRepository[LocationProductAssignment]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            LocationProductAssignment,
        )

    async def get_by_location_and_product(
        self, location_id: UUID, product_id: UUID
    ) -> LocationProductAssignment | None:
        stmt = select(LocationProductAssignment).where(
            LocationProductAssignment.location_id == location_id,
            LocationProductAssignment.product_id == product_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_location(
        self, location_id: UUID
    ) -> list[LocationProductAssignment]:
        stmt = (
            select(LocationProductAssignment)
            .options(joinedload(LocationProductAssignment.product))
            .where(LocationProductAssignment.location_id == location_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_product(
        self, product_id: UUID
    ) -> list[LocationProductAssignment]:
        stmt = (
            select(LocationProductAssignment)
            .options(joinedload(LocationProductAssignment.location))
            .where(LocationProductAssignment.product_id == product_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_location_and_product(
        self, location_id: UUID, product_id: UUID
    ) -> bool:
        assignment = await self.get_by_location_and_product(location_id, product_id)
        if assignment:
            await self.session.delete(assignment)
            await self.session.flush()
            return True
        return False
