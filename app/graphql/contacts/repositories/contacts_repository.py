from typing import Any
from uuid import UUID

from commons.db.models.user import User
from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.companies.models.company_model import Company
from app.graphql.contacts.models.contact_model import Contact
from app.graphql.contacts.strawberry.contact_landing_page_response import (
    ContactLandingPageResponse,
)
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation


class ContactsRepository(BaseRepository[Contact]):
    """Repository for Contacts entity."""

    landing_model = ContactLandingPageResponse

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Contact)

    def paginated_stmt(self) -> Select[Any]:
        """
        Build paginated query for contacts landing page.

        Returns:
            SQLAlchemy select statement with columns for landing page
        """
        return (
            select(
                Contact.id,
                Contact.created_at,
                User.full_name.label("created_by"),
                Contact.first_name,
                Contact.last_name,
                Contact.email,
                Contact.phone,
                Contact.role,
                Company.name.label("company_name"),
            )
            .select_from(Contact)
            .options(lazyload("*"))
            .join(User, User.id == Contact.created_by)
            .outerjoin(Company, Company.id == Contact.company_id)
        )

    async def get_by_company_id(self, company_id: UUID) -> list[Contact]:
        """Get all contacts for a specific company."""
        stmt = select(Contact).where(Contact.company_id == company_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job_id(self, job_id: UUID) -> list[Contact]:
        """
        Find all contacts linked to the given job ID.

        Args:
            job_id: The job ID to find contacts for

        Returns:
            List of Contact objects linked to the given job ID
        """
        stmt = select(Contact).join(
            LinkRelation,
            or_(
                # Contacts as source, Jobs as target
                (
                    (LinkRelation.source_entity_type == EntityType.CONTACT)
                    & (LinkRelation.target_entity_type == EntityType.JOB)
                    & (LinkRelation.target_entity_id == job_id)
                    & (LinkRelation.source_entity_id == Contact.id)
                ),
                # Jobs as source, Contacts as target
                (
                    (LinkRelation.source_entity_type == EntityType.JOB)
                    & (LinkRelation.target_entity_type == EntityType.CONTACT)
                    & (LinkRelation.source_entity_id == job_id)
                    & (LinkRelation.target_entity_id == Contact.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
