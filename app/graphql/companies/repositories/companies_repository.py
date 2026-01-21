from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.crm.companies.company_model import Company
from commons.db.v6.crm.companies.company_type_model import CompanyTypeEntity
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from sqlalchemy import Select, or_, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.companies.strawberry.company_landing_page_response import (
    CompanyLandingPageResponse,
)


class CompaniesRepository(BaseRepository[Company]):
    landing_model = CompanyLandingPageResponse
    rbac_resource: RbacResourceEnum | None = None
    entity_type = EntityType.COMPANY

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Company)

    def paginated_stmt(self) -> Select[Any]:
        return (
            select(
                Company.id,
                Company.created_at,
                User.full_name.label("created_by"),
                Company.name,
                CompanyTypeEntity.name.label("company_source_type"),
                Company.website,
                Company.phone,
                Company.tags,
                array([Company.created_by_id]).label("user_ids"),
            )
            .select_from(Company)
            .options(lazyload("*"))
            .join(User, User.id == Company.created_by_id)
            .join(CompanyTypeEntity, Company.company_type_id == CompanyTypeEntity.id)
        )

    async def find_by_job_id(self, job_id: UUID) -> list[Company]:
        """
        Find all companies linked to the given job ID.

        Args:
            job_id: The job ID to find companies for

        Returns:
            List of Company objects linked to the given job ID
        """
        stmt = select(Company).join(
            LinkRelation,
            or_(
                # Companies as source, Jobs as target
                (
                    (LinkRelation.source_entity_type == EntityType.COMPANY)
                    & (LinkRelation.target_entity_type == EntityType.JOB)
                    & (LinkRelation.target_entity_id == job_id)
                    & (LinkRelation.source_entity_id == Company.id)
                ),
                # Jobs as source, Companies as target
                (
                    (LinkRelation.source_entity_type == EntityType.JOB)
                    & (LinkRelation.target_entity_type == EntityType.COMPANY)
                    & (LinkRelation.source_entity_id == job_id)
                    & (LinkRelation.target_entity_id == Company.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_name(self, search_term: str, limit: int = 20) -> list[Company]:
        """
        Search companies by name using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against company name
            limit: Maximum number of companies to return (default: 20)

        Returns:
            List of Company objects matching the search criteria
        """
        stmt = (
            select(Company).where(Company.name.ilike(f"%{search_term}%")).limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_task_id(self, task_id: UUID) -> list[Company]:
        """
        Find all companies linked to the given task ID.

        Args:
            task_id: The task ID to find companies for

        Returns:
            List of Company objects linked to the given task ID
        """
        stmt = select(Company).join(
            LinkRelation,
            or_(
                # Companies as source, Tasks as target
                (
                    (LinkRelation.source_entity_type == EntityType.COMPANY)
                    & (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_id == task_id)
                    & (LinkRelation.source_entity_id == Company.id)
                ),
                # Tasks as source, Companies as target
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == EntityType.COMPANY)
                    & (LinkRelation.source_entity_id == task_id)
                    & (LinkRelation.target_entity_id == Company.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_note_id(self, note_id: UUID) -> list[Company]:
        """
        Find all companies linked to the given note ID.

        Args:
            note_id: The note ID to find companies for

        Returns:
            List of Company objects linked to the given note ID
        """
        stmt = select(Company).join(
            LinkRelation,
            or_(
                # Companies as source, Notes as target
                (
                    (LinkRelation.source_entity_type == EntityType.COMPANY)
                    & (LinkRelation.target_entity_type == EntityType.NOTE)
                    & (LinkRelation.target_entity_id == note_id)
                    & (LinkRelation.source_entity_id == Company.id)
                ),
                # Notes as source, Companies as target
                (
                    (LinkRelation.source_entity_type == EntityType.NOTE)
                    & (LinkRelation.target_entity_type == EntityType.COMPANY)
                    & (LinkRelation.source_entity_id == note_id)
                    & (LinkRelation.target_entity_id == Company.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_contact_id(self, contact_id: UUID) -> list[Company]:
        """
        Find all companies linked to the given contact ID.

        Args:
            contact_id: The contact ID to find companies for

        Returns:
            List of Company objects linked to the given contact ID
        """
        stmt = select(Company).join(
            LinkRelation,
            or_(
                # Companies as source, Contacts as target
                (
                    (LinkRelation.source_entity_type == EntityType.COMPANY)
                    & (LinkRelation.target_entity_type == EntityType.CONTACT)
                    & (LinkRelation.target_entity_id == contact_id)
                    & (LinkRelation.source_entity_id == Company.id)
                ),
                # Contacts as source, Companies as target
                (
                    (LinkRelation.source_entity_type == EntityType.CONTACT)
                    & (LinkRelation.target_entity_type == EntityType.COMPANY)
                    & (LinkRelation.source_entity_id == contact_id)
                    & (LinkRelation.target_entity_id == Company.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
