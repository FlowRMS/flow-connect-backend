"""Repository for Submittals entity with specific database operations."""

from uuid import UUID

from commons.db.v6.crm.submittals import (
    Submittal,
    SubmittalEmail,
    SubmittalItem,
    SubmittalRevision,
    SubmittalStakeholder,
    SubmittalStatus,
)
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository


class SubmittalsRepository(BaseRepository[Submittal]):
    """
    Repository for Submittals entity.

    Extends BaseRepository with submittal-specific query methods.
    """

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        """
        Initialize the Submittals repository.

        Args:
            context_wrapper: Context wrapper for user information
            session: SQLAlchemy async session
        """
        super().__init__(session, context_wrapper, Submittal)

    async def get_by_id_with_relations(self, submittal_id: UUID) -> Submittal | None:
        """
        Get a submittal by ID with all relations loaded.

        Args:
            submittal_id: UUID of the submittal

        Returns:
            Submittal model or None if not found
        """
        stmt = (
            select(Submittal)
            .options(
                selectinload(Submittal.items),
                selectinload(Submittal.stakeholders),
                selectinload(Submittal.revisions),
            )
            .where(Submittal.id == submittal_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_by_quote(self, quote_id: UUID) -> list[Submittal]:
        """
        Find all submittals for a given quote.

        Args:
            quote_id: UUID of the quote

        Returns:
            List of Submittal models
        """
        stmt = (
            select(Submittal)
            .where(Submittal.quote_id == quote_id)
            .order_by(Submittal.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_job(self, job_id: UUID) -> list[Submittal]:
        """
        Find all submittals for a given job.

        Args:
            job_id: UUID of the job

        Returns:
            List of Submittal models
        """
        stmt = (
            select(Submittal)
            .where(Submittal.job_id == job_id)
            .order_by(Submittal.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_submittals(
        self,
        search_term: str = "",
        status: SubmittalStatus | None = None,
        limit: int = 50,
    ) -> list[Submittal]:
        """
        Search submittals by term and status.

        Args:
            search_term: Term to search in submittal_number
            status: Optional status filter
            limit: Maximum number of results

        Returns:
            List of matching Submittal models
        """
        stmt = select(Submittal)

        if search_term:
            search_pattern = f"%{search_term}%"
            stmt = stmt.where(
                or_(
                    Submittal.submittal_number.ilike(search_pattern),
                    Submittal.description.ilike(search_pattern),
                )
            )

        if status:
            stmt = stmt.where(Submittal.status == status)

        stmt = stmt.limit(limit).order_by(Submittal.created_at.desc())

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_next_revision_number(self, submittal_id: UUID) -> int:
        """
        Get the next revision number for a submittal.

        Args:
            submittal_id: UUID of the submittal

        Returns:
            Next revision number
        """
        stmt = select(func.max(SubmittalRevision.revision_number)).where(
            SubmittalRevision.submittal_id == submittal_id
        )
        result = await self.session.execute(stmt)
        max_revision = result.scalar()
        return (max_revision or 0) + 1

    async def add_item(self, submittal_id: UUID, item: SubmittalItem) -> SubmittalItem:
        """
        Add an item to a submittal.

        Args:
            submittal_id: UUID of the submittal
            item: SubmittalItem to add

        Returns:
            Created SubmittalItem
        """
        submittal = await self.get_by_id(submittal_id)
        if not submittal:
            raise ValueError(f"Submittal with id {submittal_id} not found")

        submittal.items.append(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def add_stakeholder(
        self, submittal_id: UUID, stakeholder: SubmittalStakeholder
    ) -> SubmittalStakeholder:
        """
        Add a stakeholder to a submittal.

        Args:
            submittal_id: UUID of the submittal
            stakeholder: SubmittalStakeholder to add

        Returns:
            Created SubmittalStakeholder
        """
        submittal = await self.get_by_id(submittal_id)
        if not submittal:
            raise ValueError(f"Submittal with id {submittal_id} not found")

        submittal.stakeholders.append(stakeholder)
        await self.session.commit()
        await self.session.refresh(stakeholder)
        return stakeholder

    async def add_revision(
        self, submittal_id: UUID, revision: SubmittalRevision
    ) -> SubmittalRevision:
        """
        Add a revision to a submittal.

        Args:
            submittal_id: UUID of the submittal
            revision: SubmittalRevision to add

        Returns:
            Created SubmittalRevision
        """
        submittal = await self.get_by_id(submittal_id)
        if not submittal:
            raise ValueError(f"Submittal with id {submittal_id} not found")

        submittal.revisions.append(revision)
        await self.session.commit()
        await self.session.refresh(revision)
        return revision

    async def add_email(
        self, submittal_id: UUID, email: SubmittalEmail
    ) -> SubmittalEmail:
        """
        Record an email sent for a submittal.

        Args:
            submittal_id: UUID of the submittal
            email: SubmittalEmail to add

        Returns:
            Created SubmittalEmail
        """
        submittal = await self.get_by_id(submittal_id)
        if not submittal:
            raise ValueError(f"Submittal with id {submittal_id} not found")

        submittal.emails.append(email)
        await self.session.commit()
        await self.session.refresh(email)
        return email


class SubmittalItemsRepository(BaseRepository[SubmittalItem]):
    """Repository for SubmittalItem entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, SubmittalItem)


class SubmittalStakeholdersRepository(BaseRepository[SubmittalStakeholder]):
    """Repository for SubmittalStakeholder entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, SubmittalStakeholder)
