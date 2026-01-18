from commons.db.v6.crm.companies import CompanyTypeEntity
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class CompanyTypesRepository(BaseRepository[CompanyTypeEntity]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, CompanyTypeEntity)

    async def list_active(self) -> list[CompanyTypeEntity]:
        stmt = (
            select(CompanyTypeEntity)
            .where(CompanyTypeEntity.is_active.is_(True))
            .order_by(CompanyTypeEntity.display_order)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_all_ordered(self) -> list[CompanyTypeEntity]:
        stmt = select(CompanyTypeEntity).order_by(CompanyTypeEntity.display_order)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> CompanyTypeEntity | None:
        stmt = select(CompanyTypeEntity).where(CompanyTypeEntity.name == name)
        result = await self.session.execute(stmt)
        return result.scalars().first()
