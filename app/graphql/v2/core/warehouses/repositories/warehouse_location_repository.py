from uuid import UUID

from commons.db.v6 import LocationProductAssignment, WarehouseLocation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


def _recursive_children_loader(depth: int = 6):
    """
    Create recursive eager loading options for WarehouseLocation children.
    Loads children and product_assignments at each level up to the specified depth.
    Default depth of 6 covers: section -> aisle -> shelf -> bay -> row -> bin
    """
    if depth <= 0:
        # At the deepest level, still load product_assignments but don't recurse further
        return selectinload(WarehouseLocation.children).options(
            selectinload(WarehouseLocation.product_assignments),
        )

    return selectinload(WarehouseLocation.children).options(
        selectinload(WarehouseLocation.product_assignments),
        _recursive_children_loader(depth - 1),
    )


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
                selectinload(WarehouseLocation.product_assignments),
                _recursive_children_loader(),
            )
            .where(WarehouseLocation.id == location_id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[WarehouseLocation]:
        stmt = (
            select(WarehouseLocation)
            .options(
                selectinload(WarehouseLocation.product_assignments),
                _recursive_children_loader(),
            )
            .where(WarehouseLocation.warehouse_id == warehouse_id)
            .order_by(WarehouseLocation.level, WarehouseLocation.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def list_by_warehouse_with_children(
        self, warehouse_id: UUID
    ) -> list[WarehouseLocation]:
        stmt = (
            select(WarehouseLocation)
            .options(
                selectinload(WarehouseLocation.product_assignments).joinedload(
                    LocationProductAssignment.product
                ),
                _recursive_children_loader(),
            )
            .where(WarehouseLocation.warehouse_id == warehouse_id)
            .order_by(WarehouseLocation.level, WarehouseLocation.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_root_locations(self, warehouse_id: UUID) -> list[WarehouseLocation]:
        stmt = (
            select(WarehouseLocation)
            .options(
                selectinload(WarehouseLocation.product_assignments),
                _recursive_children_loader(),
            )
            .where(
                WarehouseLocation.warehouse_id == warehouse_id,
                WarehouseLocation.parent_id.is_(None),
            )
            .order_by(WarehouseLocation.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_children(self, parent_id: UUID) -> list[WarehouseLocation]:
        stmt = (
            select(WarehouseLocation)
            .options(
                selectinload(WarehouseLocation.product_assignments),
                _recursive_children_loader(),
            )
            .where(WarehouseLocation.parent_id == parent_id)
            .order_by(WarehouseLocation.sort_order)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def delete_by_warehouse(self, warehouse_id: UUID) -> None:
        stmt = select(WarehouseLocation).where(
            WarehouseLocation.warehouse_id == warehouse_id,
            WarehouseLocation.parent_id.is_(None),
        )
        result = await self.session.execute(stmt)
        for item in result.scalars().all():
            await self.session.delete(item)
        await self.session.flush()

    async def find_by_name(
        self, warehouse_id: UUID, name: str
    ) -> WarehouseLocation | None:
        stmt = select(WarehouseLocation).where(
            WarehouseLocation.warehouse_id == warehouse_id,
            WarehouseLocation.name == name,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


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
        return list(result.unique().scalars().all())

    async def list_by_product(
        self, product_id: UUID
    ) -> list[LocationProductAssignment]:
        stmt = (
            select(LocationProductAssignment)
            .options(joinedload(LocationProductAssignment.location))
            .where(LocationProductAssignment.product_id == product_id)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def delete_by_location_and_product(
        self, location_id: UUID, product_id: UUID
    ) -> bool:
        assignment = await self.get_by_location_and_product(location_id, product_id)
        if assignment:
            await self.session.delete(assignment)
            await self.session.flush()
            return True
        return False
