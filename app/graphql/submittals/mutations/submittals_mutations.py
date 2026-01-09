"""GraphQL mutations for Submittals entity."""

from uuid import UUID

import strawberry
from aioinject import Injected

from app.graphql.inject import inject
from app.graphql.submittals.services.submittals_service import SubmittalsService
from app.graphql.submittals.strawberry.submittal_input import (
    CreateSubmittalInput,
    SendSubmittalEmailInput,
    SubmittalItemInput,
    SubmittalStakeholderInput,
    UpdateSubmittalInput,
    UpdateSubmittalItemInput,
)
from app.graphql.submittals.strawberry.submittal_item_response import (
    SubmittalItemResponse,
)
from app.graphql.submittals.strawberry.submittal_response import SubmittalResponse
from app.graphql.submittals.strawberry.submittal_revision_response import (
    SubmittalRevisionResponse,
)
from app.graphql.submittals.strawberry.submittal_stakeholder_response import (
    SubmittalStakeholderResponse,
)


@strawberry.type
class SubmittalsMutations:
    """GraphQL mutations for Submittals entity."""

    @strawberry.mutation
    @inject
    async def create_submittal(
        self,
        service: Injected[SubmittalsService],
        input: CreateSubmittalInput,
    ) -> SubmittalResponse:
        """
        Create a new submittal.

        Args:
            input: Submittal creation data

        Returns:
            Created SubmittalResponse
        """
        submittal = await service.create_submittal(input)
        return SubmittalResponse.from_orm_model(submittal)

    @strawberry.mutation
    @inject
    async def update_submittal(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
        input: UpdateSubmittalInput,
    ) -> SubmittalResponse:
        """
        Update an existing submittal.

        Args:
            id: UUID of the submittal to update
            input: Update data

        Returns:
            Updated SubmittalResponse
        """
        submittal = await service.update_submittal(id, input)
        return SubmittalResponse.from_orm_model(submittal)

    @strawberry.mutation
    @inject
    async def delete_submittal(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
    ) -> bool:
        """
        Delete a submittal.

        Args:
            id: UUID of the submittal to delete

        Returns:
            True if deleted successfully
        """
        return await service.delete_submittal(id)

    # Item mutations
    @strawberry.mutation
    @inject
    async def add_submittal_item(
        self,
        service: Injected[SubmittalsService],
        submittal_id: UUID,
        input: SubmittalItemInput,
    ) -> SubmittalItemResponse:
        """
        Add an item to a submittal.

        Args:
            submittal_id: UUID of the submittal
            input: Item data

        Returns:
            Created SubmittalItemResponse
        """
        item = await service.add_item(submittal_id, input)
        return SubmittalItemResponse.from_orm_model(item)

    @strawberry.mutation
    @inject
    async def update_submittal_item(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
        input: UpdateSubmittalItemInput,
    ) -> SubmittalItemResponse:
        """
        Update a submittal item.

        Args:
            id: UUID of the item to update
            input: Update data

        Returns:
            Updated SubmittalItemResponse
        """
        item = await service.update_item(id, input)
        return SubmittalItemResponse.from_orm_model(item)

    @strawberry.mutation
    @inject
    async def remove_submittal_item(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
    ) -> bool:
        """
        Remove an item from a submittal.

        Args:
            id: UUID of the item to remove

        Returns:
            True if removed successfully
        """
        return await service.remove_item(id)

    # Stakeholder mutations
    @strawberry.mutation
    @inject
    async def add_submittal_stakeholder(
        self,
        service: Injected[SubmittalsService],
        submittal_id: UUID,
        input: SubmittalStakeholderInput,
    ) -> SubmittalStakeholderResponse:
        """
        Add a stakeholder to a submittal.

        Args:
            submittal_id: UUID of the submittal
            input: Stakeholder data

        Returns:
            Created SubmittalStakeholderResponse
        """
        stakeholder = await service.add_stakeholder(submittal_id, input)
        return SubmittalStakeholderResponse.from_orm_model(stakeholder)

    @strawberry.mutation
    @inject
    async def remove_submittal_stakeholder(
        self,
        service: Injected[SubmittalsService],
        id: UUID,
    ) -> bool:
        """
        Remove a stakeholder from a submittal.

        Args:
            id: UUID of the stakeholder to remove

        Returns:
            True if removed successfully
        """
        return await service.remove_stakeholder(id)

    # Revision mutations
    @strawberry.mutation
    @inject
    async def create_submittal_revision(
        self,
        service: Injected[SubmittalsService],
        submittal_id: UUID,
        notes: str | None = None,
    ) -> SubmittalRevisionResponse:
        """
        Create a new revision for a submittal.

        Args:
            submittal_id: UUID of the submittal
            notes: Optional notes for the revision

        Returns:
            Created SubmittalRevisionResponse
        """
        revision = await service.create_revision(submittal_id, notes)
        return SubmittalRevisionResponse.from_orm_model(revision)

    # Email mutations
    @strawberry.mutation
    @inject
    async def send_submittal_email(
        self,
        service: Injected[SubmittalsService],
        input: SendSubmittalEmailInput,
    ) -> bool:
        """
        Send an email for a submittal.

        Args:
            input: Email data

        Returns:
            True if email was recorded successfully
        """
        await service.send_email(input)
        return True
