from uuid import UUID

from commons.db.v6 import LocationProductAssignment
from sqlalchemy import and_, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


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
