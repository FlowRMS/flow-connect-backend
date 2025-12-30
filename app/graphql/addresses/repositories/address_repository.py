from uuid import UUID

from commons.db.v6.core.addresses.address import Address, AddressSourceTypeEnum
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class AddressRepository(BaseRepository[Address]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
    ) -> None:
        super().__init__(session, context_wrapper, Address)

    async def list_by_source(
        self,
        source_type: AddressSourceTypeEnum,
        source_id: UUID,
    ) -> list[Address]:
        stmt = select(Address).where(
            Address.source_type == source_type,
            Address.source_id == source_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_source_id(self, source_id: UUID) -> list[Address]:
        stmt = select(Address).where(Address.source_id == source_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
