from commons.db.v6 import Organization
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, Organization)

    async def get_single(self) -> Organization | None:
        stmt = select(Organization).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def organization_exists(self) -> bool:
        stmt = select(Organization).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
