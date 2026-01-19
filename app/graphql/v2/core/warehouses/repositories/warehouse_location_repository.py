from uuid import UUID

from commons.db.v6 import LocationProductAssignment, WarehouseLocation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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

    @property
    def base_query(self):
        """Base query with standard eager loading for locations."""
        return select(WarehouseLocation).options(
            selectinload(WarehouseLocation.product_assignments).joinedload(
                LocationProductAssignment.product
            ),
            _recursive_children_loader(),
        )

    async def get_by_id_with_children(
        self, location_id: UUID
    ) -> WarehouseLocation | None:
        stmt = self.base_query.where(WarehouseLocation.id == location_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[WarehouseLocation]:
        stmt = self.base_query.where(
            WarehouseLocation.warehouse_id == warehouse_id
        ).order_by(WarehouseLocation.level, WarehouseLocation.sort_order)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_root_locations(self, warehouse_id: UUID) -> list[WarehouseLocation]:
        stmt = self.base_query.where(
            WarehouseLocation.warehouse_id == warehouse_id,
            WarehouseLocation.parent_id.is_(None),
        ).order_by(WarehouseLocation.sort_order)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_children(self, parent_id: UUID) -> list[WarehouseLocation]:
        stmt = self.base_query.where(WarehouseLocation.parent_id == parent_id).order_by(
            WarehouseLocation.sort_order
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

    async def find_by_name(
        self, warehouse_id: UUID, name: str
    ) -> WarehouseLocation | None:
        stmt = select(WarehouseLocation).where(
            WarehouseLocation.warehouse_id == warehouse_id,
            WarehouseLocation.name == name,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
