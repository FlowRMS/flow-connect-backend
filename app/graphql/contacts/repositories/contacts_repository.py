from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.contacts.models.contact_model import Contact


class ContactsRepository(BaseRepository[Contact]):
    """Repository for Contacts entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Contact)

    async def get_by_company_id(self, company_id: UUID) -> list[Contact]:
        """Get all contacts for a specific company."""
        stmt = select(Contact).where(Contact.company_id == company_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
