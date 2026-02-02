from uuid import UUID

from commons.db.v6 import RbacResourceEnum
from commons.db.v6.core.sales_teams.sales_team import SalesTeam
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.core.processors.executor import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService


class SalesTeamRepository(BaseRepository[SalesTeam]):
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.ADMIN

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
            SalesTeam,
            rbac_filter_service,
            processor_executor,
        )

    async def get_by_name(self, name: str) -> SalesTeam | None:
        stmt = select(SalesTeam).where(SalesTeam.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def name_exists(self, name: str, exclude_id: UUID | None = None) -> bool:
        stmt = select(func.count()).where(SalesTeam.name == name)
        if exclude_id:
            stmt = stmt.where(SalesTeam.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one() > 0

    async def get_by_territory(self, territory_id: UUID) -> SalesTeam | None:
        stmt = select(SalesTeam).where(SalesTeam.territory_id == territory_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_manager(self, manager_id: UUID) -> list[SalesTeam]:
        stmt = (
            select(SalesTeam)
            .where(SalesTeam.manager_id == manager_id)
            .order_by(SalesTeam.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_active(self) -> list[SalesTeam]:
        stmt = (
            select(SalesTeam).where(SalesTeam.active.is_(True)).order_by(SalesTeam.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
