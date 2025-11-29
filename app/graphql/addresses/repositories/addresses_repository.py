from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.addresses.models.address_model import CompanyAddress
from app.graphql.base_repository import BaseRepository


class AddressesRepository(BaseRepository[CompanyAddress]):
    """Repository for Addresses entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, CompanyAddress)

    async def get_by_company_id(self, company_id: UUID) -> list[CompanyAddress]:
        """Get all addresses for a specific company."""
        stmt = select(CompanyAddress).where(CompanyAddress.company_id == company_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
