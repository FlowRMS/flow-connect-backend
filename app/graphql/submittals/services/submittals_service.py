"""Service layer for Submittals business logic."""

from uuid import UUID

from commons.db.v6.crm.submittals import (
    Submittal,
    SubmittalEmail,
    SubmittalItem,
    SubmittalItemApprovalStatus,
    SubmittalItemMatchStatus,
    SubmittalRevision,
    SubmittalStakeholder,
    SubmittalStatus,
)
from loguru import logger

from app.graphql.submittals.repositories.submittals_repository import (
    SubmittalItemsRepository,
    SubmittalStakeholdersRepository,
    SubmittalsRepository,
)
from app.graphql.submittals.strawberry.submittal_input import (
    CreateSubmittalInput,
    SendSubmittalEmailInput,
    SubmittalItemInput,
    SubmittalStakeholderInput,
    UpdateSubmittalInput,
    UpdateSubmittalItemInput,
)


class SubmittalsService:
    """Service for Submittals business logic."""

    def __init__(
        self,
        repository: SubmittalsRepository,
        items_repository: SubmittalItemsRepository,
        stakeholders_repository: SubmittalStakeholdersRepository,
    ) -> None:
        """
        Initialize the Submittals service.

        Args:
            repository: Submittals repository instance
            items_repository: SubmittalItems repository instance
            stakeholders_repository: SubmittalStakeholders repository instance
        """
        self.repository = repository
        self.items_repository = items_repository
        self.stakeholders_repository = stakeholders_repository

    async def create_submittal(self, input_data: CreateSubmittalInput) -> Submittal:
        """
        Create a new submittal.

        Args:
            input_data: Submittal creation data

        Returns:
            Created Submittal model
        """
        submittal = input_data.to_orm_model()
        created = await self.repository.create(submittal)
        logger.info(f"Created submittal {created.id} with number {created.submittal_number}")
        return created

    async def update_submittal(
        self, submittal_id: UUID, input_data: UpdateSubmittalInput
    ) -> Submittal:
        """
        Update an existing submittal.

        Args:
            submittal_id: UUID of the submittal to update
            input_data: Update data

        Returns:
            Updated Submittal model

        Raises:
            ValueError: If submittal not found
        """
        submittal = await self.repository.get_by_id(submittal_id)
        if not submittal:
            raise ValueError(f"Submittal with id {submittal_id} not found")

        if input_data.status is not None:
            submittal.status = SubmittalStatus(input_data.status.value)

        if input_data.transmittal_purpose is not None:
            from commons.db.v6.crm.submittals import TransmittalPurpose

            submittal.transmittal_purpose = TransmittalPurpose(
                input_data.transmittal_purpose.value
            )

        if input_data.description is not None:
            submittal.description = input_data.description

        updated = await self.repository.update(submittal)
        logger.info(f"Updated submittal {submittal_id}")
        return updated

    async def delete_submittal(self, submittal_id: UUID) -> bool:
        """
        Delete a submittal.

        Args:
            submittal_id: UUID of the submittal to delete

        Returns:
            True if deleted successfully
        """
        result = await self.repository.delete(submittal_id)
        if result:
            logger.info(f"Deleted submittal {submittal_id}")
        return result

    async def get_submittal(self, submittal_id: UUID) -> Submittal | None:
        """
        Get a submittal by ID.

        Args:
            submittal_id: UUID of the submittal

        Returns:
            Submittal model or None if not found
        """
        return await self.repository.get_by_id_with_relations(submittal_id)

    async def get_submittals_by_quote(self, quote_id: UUID) -> list[Submittal]:
        """
        Get all submittals for a quote.

        Args:
            quote_id: UUID of the quote

        Returns:
            List of Submittal models
        """
        return await self.repository.find_by_quote(quote_id)

    async def get_submittals_by_job(self, job_id: UUID) -> list[Submittal]:
        """
        Get all submittals for a job.

        Args:
            job_id: UUID of the job

        Returns:
            List of Submittal models
        """
        return await self.repository.find_by_job(job_id)

    async def search_submittals(
        self,
        search_term: str = "",
        status: SubmittalStatus | None = None,
        limit: int = 50,
    ) -> list[Submittal]:
        """
        Search submittals.

        Args:
            search_term: Search term for submittal_number
            status: Optional status filter
            limit: Maximum number of results

        Returns:
            List of matching Submittal models
        """
        return await self.repository.search_submittals(search_term, status, limit)

    # Item operations
    async def add_item(
        self, submittal_id: UUID, input_data: SubmittalItemInput
    ) -> SubmittalItem:
        """
        Add an item to a submittal.

        Args:
            submittal_id: UUID of the submittal
            input_data: Item data

        Returns:
            Created SubmittalItem
        """
        item = input_data.to_orm_model()
        created = await self.repository.add_item(submittal_id, item)
        logger.info(f"Added item {created.id} to submittal {submittal_id}")
        return created

    async def update_item(
        self, item_id: UUID, input_data: UpdateSubmittalItemInput
    ) -> SubmittalItem:
        """
        Update a submittal item.

        Args:
            item_id: UUID of the item to update
            input_data: Update data

        Returns:
            Updated SubmittalItem

        Raises:
            ValueError: If item not found
        """
        item = await self.items_repository.get_by_id(item_id)
        if not item:
            raise ValueError(f"SubmittalItem with id {item_id} not found")

        if input_data.spec_sheet_id is not None:
            item.spec_sheet_id = input_data.spec_sheet_id

        if input_data.highlight_version_id is not None:
            item.highlight_version_id = input_data.highlight_version_id

        if input_data.part_number is not None:
            item.part_number = input_data.part_number

        if input_data.description is not None:
            item.description = input_data.description

        if input_data.quantity is not None:
            item.quantity = input_data.quantity

        if input_data.approval_status is not None:
            item.approval_status = SubmittalItemApprovalStatus(
                input_data.approval_status.value
            )

        if input_data.match_status is not None:
            item.match_status = SubmittalItemMatchStatus(input_data.match_status.value)

        if input_data.notes is not None:
            item.notes = input_data.notes

        updated = await self.items_repository.update(item)
        logger.info(f"Updated submittal item {item_id}")
        return updated

    async def remove_item(self, item_id: UUID) -> bool:
        """
        Remove an item from a submittal.

        Args:
            item_id: UUID of the item to remove

        Returns:
            True if removed successfully
        """
        result = await self.items_repository.delete(item_id)
        if result:
            logger.info(f"Removed submittal item {item_id}")
        return result

    # Stakeholder operations
    async def add_stakeholder(
        self, submittal_id: UUID, input_data: SubmittalStakeholderInput
    ) -> SubmittalStakeholder:
        """
        Add a stakeholder to a submittal.

        Args:
            submittal_id: UUID of the submittal
            input_data: Stakeholder data

        Returns:
            Created SubmittalStakeholder
        """
        stakeholder = input_data.to_orm_model()
        created = await self.repository.add_stakeholder(submittal_id, stakeholder)
        logger.info(f"Added stakeholder {created.id} to submittal {submittal_id}")
        return created

    async def remove_stakeholder(self, stakeholder_id: UUID) -> bool:
        """
        Remove a stakeholder from a submittal.

        Args:
            stakeholder_id: UUID of the stakeholder to remove

        Returns:
            True if removed successfully
        """
        result = await self.stakeholders_repository.delete(stakeholder_id)
        if result:
            logger.info(f"Removed stakeholder {stakeholder_id}")
        return result

    # Revision operations
    async def create_revision(
        self, submittal_id: UUID, notes: str | None = None
    ) -> SubmittalRevision:
        """
        Create a new revision for a submittal.

        Args:
            submittal_id: UUID of the submittal
            notes: Optional notes for the revision

        Returns:
            Created SubmittalRevision
        """
        next_revision = await self.repository.get_next_revision_number(submittal_id)

        revision = SubmittalRevision(
            revision_number=next_revision,
            notes=notes,
        )

        created = await self.repository.add_revision(submittal_id, revision)
        logger.info(
            f"Created revision {created.revision_number} for submittal {submittal_id}"
        )
        return created

    # Email operations
    async def send_email(self, input_data: SendSubmittalEmailInput) -> SubmittalEmail:
        """
        Record a sent email for a submittal.

        Note: Actual email sending should be handled by an email service.
        This method records the email in the database.

        Args:
            input_data: Email data

        Returns:
            Created SubmittalEmail
        """
        email = SubmittalEmail(
            revision_id=input_data.revision_id,
            subject=input_data.subject,
            body=input_data.body,
            recipient_emails=input_data.recipient_emails,
            recipients=[{"email": e, "type": "to"} for e in input_data.recipient_emails],
        )

        created = await self.repository.add_email(input_data.submittal_id, email)
        logger.info(
            f"Recorded email for submittal {input_data.submittal_id} to {len(input_data.recipient_emails)} recipients"
        )
        return created
