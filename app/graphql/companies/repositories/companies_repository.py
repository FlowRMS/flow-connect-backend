from typing import Any
from uuid import UUID

from commons.db.models.user import User
from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import lazyload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.companies.models.company_model import Company
from app.graphql.companies.strawberry.company_landing_page_response import (
    CompanyLandingPageResponse,
)
from app.graphql.links.models.entity_type import EntityType
from app.graphql.links.models.link_relation_model import LinkRelation


class CompaniesRepository(BaseRepository[Company]):
    """Repository for Companies entity."""

    landing_model = CompanyLandingPageResponse

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, Company)

    def paginated_stmt(self) -> Select[Any]:
        """
        Build paginated query for companies landing page.

        Returns:
            SQLAlchemy select statement with columns for landing page
        """
        return (
            select(
                Company.id,
                Company.created_at,
                User.full_name.label("created_by"),
                Company.name,
                Company.company_source_type,
                Company.website,
                Company.phone,
            )
            .select_from(Company)
            .options(lazyload("*"))
            .join(User, User.id == Company.created_by)
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
