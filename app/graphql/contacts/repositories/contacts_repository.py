from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.crm.companies.company_model import Company
from commons.db.v6.crm.contact_model import Contact
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from sqlalchemy import Select, or_, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.contacts.strawberry.contact_landing_page_response import (
    ContactLandingPageResponse,
)


class ContactsRepository(BaseRepository[Contact]):
    landing_model = ContactLandingPageResponse
    rbac_resource: RbacResourceEnum | None = None
    entity_type = EntityType.CONTACT

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Contact)

    def paginated_stmt(self) -> Select[Any]:
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
                Contact.tags,
                array([Contact.created_by_id]).label("user_ids"),
            )
            .select_from(Contact)
            .options(lazyload("*"))
            .join(User, User.id == Contact.created_by_id)
            .outerjoin(
                LinkRelation,
                or_(
                    (
                        (LinkRelation.source_entity_type == EntityType.CONTACT)
                        & (LinkRelation.target_entity_type == EntityType.COMPANY)
                        & (LinkRelation.source_entity_id == Contact.id)
                    ),
                    (
                        (LinkRelation.source_entity_type == EntityType.COMPANY)
                        & (LinkRelation.target_entity_type == EntityType.CONTACT)
                        & (LinkRelation.target_entity_id == Contact.id)
                    ),
                ),
            )
            .outerjoin(
                Company,
                or_(
                    (
                        (LinkRelation.source_entity_type == EntityType.CONTACT)
                        & (LinkRelation.target_entity_type == EntityType.COMPANY)
                        & (Company.id == LinkRelation.target_entity_id)
                    ),
                    (
                        (LinkRelation.source_entity_type == EntityType.COMPANY)
                        & (LinkRelation.target_entity_type == EntityType.CONTACT)
                        & (Company.id == LinkRelation.source_entity_id)
                    ),
                ),
            )
        )

    async def get_by_company_id(self, company_id: UUID) -> list[Contact]:
        """
        Get all contacts for a specific company.

        Finds contacts that are either:
        - Directly linked via Contact.company_id
        - Linked via LinkRelation table (company <-> contact)
        """
        stmt = (
            select(Contact)
            .distinct()
            .join(
                LinkRelation,
                or_(
                    # Contact as source, Company as target
                    (
                        (LinkRelation.source_entity_type == EntityType.CONTACT)
                        & (LinkRelation.target_entity_type == EntityType.COMPANY)
                        & (LinkRelation.target_entity_id == company_id)
                        & (LinkRelation.source_entity_id == Contact.id)
                    ),
                    # Company as source, Contact as target
                    (
                        (LinkRelation.source_entity_type == EntityType.COMPANY)
                        & (LinkRelation.target_entity_type == EntityType.CONTACT)
                        & (LinkRelation.source_entity_id == company_id)
                        & (LinkRelation.target_entity_id == Contact.id)
                    ),
                ),
            )
        )
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

    async def search_by_name(self, search_term: str, limit: int = 20) -> list[Contact]:
        """
        Search contacts by first name or last name using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against contact names
            limit: Maximum number of contacts to return (default: 20)

        Returns:
            List of Contact objects matching the search criteria
        """
        stmt = (
            select(Contact)
            .where(
                or_(
                    Contact.first_name.ilike(f"%{search_term}%"),
                    Contact.last_name.ilike(f"%{search_term}%"),
                )
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_task_id(self, task_id: UUID) -> list[Contact]:
        """
        Find all contacts linked to the given task ID.

        Args:
            task_id: The task ID to find contacts for

        Returns:
            List of Contact objects linked to the given task ID
        """
        stmt = select(Contact).join(
            LinkRelation,
            or_(
                # Contacts as source, Tasks as target
                (
                    (LinkRelation.source_entity_type == EntityType.CONTACT)
                    & (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_id == task_id)
                    & (LinkRelation.source_entity_id == Contact.id)
                ),
                # Tasks as source, Contacts as target
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == EntityType.CONTACT)
                    & (LinkRelation.source_entity_id == task_id)
                    & (LinkRelation.target_entity_id == Contact.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_note_id(self, note_id: UUID) -> list[Contact]:
        """
        Find all contacts linked to the given note ID.

        Args:
            note_id: The note ID to find contacts for

        Returns:
            List of Contact objects linked to the given note ID
        """
        stmt = select(Contact).join(
            LinkRelation,
            or_(
                # Contacts as source, Notes as target
                (
                    (LinkRelation.source_entity_type == EntityType.CONTACT)
                    & (LinkRelation.target_entity_type == EntityType.NOTE)
                    & (LinkRelation.target_entity_id == note_id)
                    & (LinkRelation.source_entity_id == Contact.id)
                ),
                # Notes as source, Contacts as target
                (
                    (LinkRelation.source_entity_type == EntityType.NOTE)
                    & (LinkRelation.target_entity_type == EntityType.CONTACT)
                    & (LinkRelation.source_entity_id == note_id)
                    & (LinkRelation.target_entity_id == Contact.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
