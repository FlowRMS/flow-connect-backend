from typing import Any
from uuid import UUID

from commons.db.v6 import RbacResourceEnum, User
from commons.db.v6.crm.jobs.job_status_model import JobStatus
from commons.db.v6.crm.jobs.jobs_model import Job
from sqlalchemy import Select, func, or_, select
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.jobs.strawberry.job_landing_page_response import (
    JobLandingPageResponse,
)


class JobsRepository(BaseRepository[Job]):
    landing_model = JobLandingPageResponse
    rbac_resource: RbacResourceEnum | None = RbacResourceEnum.JOB

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        """
        Initialize the Jobs repository.

        Args:
            session: SQLAlchemy async session
        """
        super().__init__(session, context_wrapper, Job)

    def paginated_stmt(self) -> Select[Any]:
        user_owner_alias = aliased(User)
        requester_alias = aliased(User)
        return (
            select(
                Job.id,
                Job.created_at,
                User.full_name.label("created_by"),
                Job.job_name,
                JobStatus.name.label("status_name"),
                Job.start_date,
                Job.end_date,
                Job.description,
                Job.job_type,
                requester_alias.full_name.label("requester"),
                user_owner_alias.full_name.label("job_owner"),
                Job.tags,
                array([Job.created_by_id]).label("user_ids"),
            )
            .select_from(Job)
            .options(lazyload("*"))
            .join(JobStatus, JobStatus.id == Job.status_id)
            .join(User, User.id == Job.created_by_id)
            .outerjoin(user_owner_alias, user_owner_alias.id == Job.job_owner_id)
            .outerjoin(requester_alias, requester_alias.id == Job.requester_id)
        )

    async def name_exists(self, job_name: str) -> bool:
        """
        Check if a job with the given name already exists.

        Args:
            job_name: The job name to check

        Returns:
            True if a job with this name exists, False otherwise
        """
        result = await self.session.execute(
            select(func.count()).select_from(Job).where(Job.job_name == job_name)
        )
        return result.scalar_one() > 0

    async def search_by_name(self, search_term: str, limit: int = 20) -> list[Job]:
        """
        Search jobs by name using case-insensitive pattern matching.

        Args:
            search_term: The search term to match against job name
            limit: Maximum number of jobs to return (default: 20)

        Returns:
            List of Job objects matching the search criteria
        """
        stmt = select(Job).where(Job.job_name.ilike(f"%{search_term}%")).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_contact_id(self, contact_id: UUID) -> list[Job]:
        """
        Find all jobs linked to the given contact ID.

        Args:
            contact_id: The contact ID to find jobs for

        Returns:
            List of Job objects linked to the given contact ID
        """
        from commons.db.v6.crm.links.entity_type import EntityType
        from commons.db.v6.crm.links.link_relation_model import LinkRelation

        stmt = select(Job).join(
            LinkRelation,
            or_(
                # Jobs as source, Contacts as target
                (
                    (LinkRelation.source_entity_type == EntityType.JOB)
                    & (LinkRelation.target_entity_type == EntityType.CONTACT)
                    & (LinkRelation.target_entity_id == contact_id)
                    & (LinkRelation.source_entity_id == Job.id)
                ),
                # Contacts as source, Jobs as target
                (
                    (LinkRelation.source_entity_type == EntityType.CONTACT)
                    & (LinkRelation.target_entity_type == EntityType.JOB)
                    & (LinkRelation.source_entity_id == contact_id)
                    & (LinkRelation.target_entity_id == Job.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_company_id(self, company_id: UUID) -> list[Job]:
        """
        Find all jobs linked to the given company ID.

        Args:
            company_id: The company ID to find jobs for

        Returns:
            List of Job objects linked to the given company ID
        """
        from commons.db.v6.crm.links.entity_type import EntityType
        from commons.db.v6.crm.links.link_relation_model import LinkRelation

        stmt = select(Job).join(
            LinkRelation,
            or_(
                # Jobs as source, Companies as target
                (
                    (LinkRelation.source_entity_type == EntityType.JOB)
                    & (LinkRelation.target_entity_type == EntityType.COMPANY)
                    & (LinkRelation.target_entity_id == company_id)
                    & (LinkRelation.source_entity_id == Job.id)
                ),
                # Companies as source, Jobs as target
                (
                    (LinkRelation.source_entity_type == EntityType.COMPANY)
                    & (LinkRelation.target_entity_type == EntityType.JOB)
                    & (LinkRelation.source_entity_id == company_id)
                    & (LinkRelation.target_entity_id == Job.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_task_id(self, task_id: UUID) -> list[Job]:
        """
        Find all jobs linked to the given task ID.

        Args:
            task_id: The task ID to find jobs for

        Returns:
            List of Job objects linked to the given task ID
        """
        from commons.db.v6.crm.links.entity_type import EntityType
        from commons.db.v6.crm.links.link_relation_model import LinkRelation

        stmt = select(Job).join(
            LinkRelation,
            or_(
                # Jobs as source, Tasks as target
                (
                    (LinkRelation.source_entity_type == EntityType.JOB)
                    & (LinkRelation.target_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_id == task_id)
                    & (LinkRelation.source_entity_id == Job.id)
                ),
                # Tasks as source, Jobs as target
                (
                    (LinkRelation.source_entity_type == EntityType.TASK)
                    & (LinkRelation.target_entity_type == EntityType.JOB)
                    & (LinkRelation.source_entity_id == task_id)
                    & (LinkRelation.target_entity_id == Job.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_note_id(self, note_id: UUID) -> list[Job]:
        """
        Find all jobs linked to the given note ID.

        Args:
            note_id: The note ID to find jobs for

        Returns:
            List of Job objects linked to the given note ID
        """
        from commons.db.v6.crm.links.entity_type import EntityType
        from commons.db.v6.crm.links.link_relation_model import LinkRelation

        stmt = select(Job).join(
            LinkRelation,
            or_(
                # Jobs as source, Notes as target
                (
                    (LinkRelation.source_entity_type == EntityType.JOB)
                    & (LinkRelation.target_entity_type == EntityType.NOTE)
                    & (LinkRelation.target_entity_id == note_id)
                    & (LinkRelation.source_entity_id == Job.id)
                ),
                # Notes as source, Jobs as target
                (
                    (LinkRelation.source_entity_type == EntityType.NOTE)
                    & (LinkRelation.target_entity_type == EntityType.JOB)
                    & (LinkRelation.source_entity_id == note_id)
                    & (LinkRelation.target_entity_id == Job.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
