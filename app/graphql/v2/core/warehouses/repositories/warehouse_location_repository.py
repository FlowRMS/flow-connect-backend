from uuid import UUID

from commons.db.v6 import LocationProductAssignment, WarehouseLocation
from sqlalchemy import and_, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


def _recursive_children_loader(depth: int = 6):
    """
    Create recursive eager loading options for WarehouseLocation children.
    Loads children and product_assignments (with product details) at each level up to the specified depth.
    Default depth of 6 covers: section -> aisle -> shelf -> bay -> row -> bin
    """
    if depth <= 0:
        # At the deepest level, still load product_assignments with product but don't recurse further
        return selectinload(WarehouseLocation.children).options(
            selectinload(WarehouseLocation.product_assignments).joinedload(
                LocationProductAssignment.product
            ),
        )

    return selectinload(WarehouseLocation.children).options(
        selectinload(WarehouseLocation.product_assignments).joinedload(
            LocationProductAssignment.product
        ),
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
                selectinload(WarehouseLocation.product_assignments).joinedload(
                    LocationProductAssignment.product
                ),
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
                selectinload(WarehouseLocation.product_assignments).joinedload(
                    LocationProductAssignment.product
                ),
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
                selectinload(WarehouseLocation.product_assignments).joinedload(
                    LocationProductAssignment.product
                ),
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

    async def get_with_product(
        self, assignment_id: UUID
    ) -> LocationProductAssignment | None:
        """Get assignment by ID with product relationship loaded."""
        stmt = (
            select(LocationProductAssignment)
            .options(joinedload(LocationProductAssignment.product))
            .where(LocationProductAssignment.id == assignment_id)
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

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

    async def get_by_location_product_pairs(
        self, pairs: list[tuple[UUID, UUID]]
    ) -> dict[tuple[UUID, UUID], LocationProductAssignment]:
        """Batch fetch assignments by (location_id, product_id) pairs.

        Returns a dict mapping (location_id, product_id) -> assignment for efficient lookup.
        """
        if not pairs:
            return {}

        # Build OR conditions for each pair
        conditions = [
            and_(
                LocationProductAssignment.location_id == loc_id,
                LocationProductAssignment.product_id == prod_id,
            )
            for loc_id, prod_id in pairs
        ]

        stmt = select(LocationProductAssignment).where(or_(*conditions))
        result = await self.session.execute(stmt)
        assignments = result.scalars().all()

        return {(a.location_id, a.product_id): a for a in assignments}

    async def get_many_with_product(
        self, assignment_ids: list[UUID]
    ) -> list[LocationProductAssignment]:
        """Batch fetch assignments by IDs with product relationship loaded."""
        if not assignment_ids:
            return []

        stmt = (
            select(LocationProductAssignment)
            .options(joinedload(LocationProductAssignment.product))
            .where(LocationProductAssignment.id.in_(assignment_ids))
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def bulk_delete_by_location_product_pairs(
        self, pairs: list[tuple[UUID, UUID]]
    ) -> int:
        """Bulk delete assignments by (location_id, product_id) pairs in a single query.

        Returns the number of deleted rows.
        """
        if not pairs:
            return 0

        # Build OR conditions for each pair
        conditions = [
            and_(
                LocationProductAssignment.location_id == loc_id,
                LocationProductAssignment.product_id == prod_id,
            )
            for loc_id, prod_id in pairs
        ]

        stmt = delete(LocationProductAssignment).where(or_(*conditions))
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount or 0  # type: ignore[return-value]
