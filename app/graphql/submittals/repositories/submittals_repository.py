from uuid import UUID

from commons.db.v6.crm.spec_sheets.spec_sheet_highlight_model import (
    SpecSheetHighlightVersion,
)
from commons.db.v6.crm.submittals import (
    Submittal,
    SubmittalChangeAnalysis,
    SubmittalEmail,
    SubmittalItem,
    SubmittalItemChange,
    SubmittalReturnedPdf,
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
                selectinload(Submittal.items)
                .selectinload(SubmittalItem.highlight_version)
                .selectinload(SpecSheetHighlightVersion.regions),
                selectinload(Submittal.stakeholders),
                selectinload(Submittal.revisions).selectinload(SubmittalRevision.emails),
                selectinload(Submittal.created_by),
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
            .options(selectinload(Submittal.created_by))
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
            .options(selectinload(Submittal.created_by))
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
        stmt = select(Submittal).options(selectinload(Submittal.created_by))

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
        await self.session.flush()
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
        await self.session.flush()
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

        # Set created_by_id from context (required by HasCreatedBy mixin)
        revision.created_by_id = self.context.auth_info.flow_user_id

        submittal.revisions.append(revision)
        await self.session.flush()
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
        await self.session.flush()
        return email


class SubmittalItemsRepository(BaseRepository[SubmittalItem]):
    """Repository for SubmittalItem entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, SubmittalItem)


class SubmittalStakeholdersRepository(BaseRepository[SubmittalStakeholder]):
    """Repository for SubmittalStakeholder entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, SubmittalStakeholder)


class SubmittalRevisionsRepository(BaseRepository[SubmittalRevision]):
    """Repository for SubmittalRevision entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, SubmittalRevision)

    async def get_by_id_with_returned_pdfs(
        self, revision_id: UUID
    ) -> SubmittalRevision | None:
        """Get a revision by ID with returned PDFs loaded."""
        stmt = (
            select(SubmittalRevision)
            .options(
                selectinload(SubmittalRevision.returned_pdfs)
                .selectinload(SubmittalReturnedPdf.change_analysis)
                .selectinload(SubmittalChangeAnalysis.item_changes),
            )
            .where(SubmittalRevision.id == revision_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_returned_pdf(
        self, revision_id: UUID, returned_pdf: SubmittalReturnedPdf
    ) -> SubmittalReturnedPdf:
        """Add a returned PDF to a revision."""
        revision = await self.get_by_id(revision_id)
        if not revision:
            raise ValueError(f"SubmittalRevision with id {revision_id} not found")

        returned_pdf.created_by_id = self.context.auth_info.flow_user_id
        revision.returned_pdfs.append(returned_pdf)
        await self.session.flush()
        return returned_pdf


class SubmittalReturnedPdfsRepository(BaseRepository[SubmittalReturnedPdf]):
    """Repository for SubmittalReturnedPdf entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, SubmittalReturnedPdf)

    async def get_by_id_with_analysis(
        self, returned_pdf_id: UUID
    ) -> SubmittalReturnedPdf | None:
        """Get a returned PDF by ID with change analysis and item changes loaded."""
        stmt = (
            select(SubmittalReturnedPdf)
            .options(
                selectinload(SubmittalReturnedPdf.change_analysis).selectinload(
                    SubmittalChangeAnalysis.item_changes
                ),
            )
            .where(SubmittalReturnedPdf.id == returned_pdf_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_change_analysis(
        self, returned_pdf_id: UUID, change_analysis: SubmittalChangeAnalysis
    ) -> SubmittalChangeAnalysis:
        """Add a change analysis to a returned PDF."""
        returned_pdf = await self.get_by_id(returned_pdf_id)
        if not returned_pdf:
            raise ValueError(
                f"SubmittalReturnedPdf with id {returned_pdf_id} not found"
            )

        if returned_pdf.change_analysis is not None:
            raise ValueError(
                f"SubmittalReturnedPdf {returned_pdf_id} already has a change analysis"
            )

        returned_pdf.change_analysis = change_analysis
        await self.session.flush()
        return change_analysis


class SubmittalChangeAnalysisRepository(BaseRepository[SubmittalChangeAnalysis]):
    """Repository for SubmittalChangeAnalysis entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, SubmittalChangeAnalysis)

    async def get_by_id_with_item_changes(
        self, analysis_id: UUID
    ) -> SubmittalChangeAnalysis | None:
        """Get a change analysis by ID with item changes loaded."""
        stmt = (
            select(SubmittalChangeAnalysis)
            .options(selectinload(SubmittalChangeAnalysis.item_changes))
            .where(SubmittalChangeAnalysis.id == analysis_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_item_change(
        self, analysis_id: UUID, item_change: SubmittalItemChange
    ) -> SubmittalItemChange:
        """Add an item change to a change analysis."""
        analysis = await self.get_by_id(analysis_id)
        if not analysis:
            raise ValueError(f"SubmittalChangeAnalysis with id {analysis_id} not found")

        analysis.item_changes.append(item_change)
        analysis.total_changes_detected = len(analysis.item_changes)
        await self.session.flush()
        return item_change


class SubmittalItemChangesRepository(BaseRepository[SubmittalItemChange]):
    """Repository for SubmittalItemChange entity."""

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, SubmittalItemChange)
