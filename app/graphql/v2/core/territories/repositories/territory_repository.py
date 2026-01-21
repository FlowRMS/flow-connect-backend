from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.core.territories.territory import Territory
from commons.db.v6.core.territories.territory_type_enum import TerritoryTypeEnum
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.core.processors.executor import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService


class TerritoryRepository(BaseRepository[Territory]):
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.TERRITORY

    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        rbac_filter_service: RbacFilterService,
        processor_executor: ProcessorExecutor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            Territory,
            rbac_filter_service,
            processor_executor,
        )

    async def get_by_code(self, code: str) -> Territory | None:
        stmt = select(Territory).where(Territory.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def code_exists(self, code: str, exclude_id: UUID | None = None) -> bool:
        stmt = select(func.count()).where(Territory.code == code)
        if exclude_id:
            stmt = stmt.where(Territory.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0

    async def get_by_type(
        self, territory_type: TerritoryTypeEnum, active_only: bool = True
    ) -> list[Territory]:
        stmt = select(Territory).where(Territory.territory_type == territory_type)
        if active_only:
            stmt = stmt.where(Territory.active.is_(True))
        stmt = stmt.order_by(Territory.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_children(self, parent_id: UUID) -> list[Territory]:
        stmt = (
            select(Territory)
            .where(Territory.parent_id == parent_id)
            .order_by(Territory.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_hierarchy(self, territory_id: UUID) -> list[Territory]:
        hierarchy: list[Territory] = []
        current_id: UUID | None = territory_id

        while current_id:
            stmt = select(Territory).where(Territory.id == current_id)
            result = await self.session.execute(stmt)
            territory = result.scalar_one_or_none()

            if territory:
                hierarchy.append(territory)
                current_id = territory.parent_id
            else:
                break

        return hierarchy

    async def get_all_active(self) -> list[Territory]:
        stmt = (
            select(Territory)
            .where(Territory.active.is_(True))
            .order_by(Territory.territory_type, Territory.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
