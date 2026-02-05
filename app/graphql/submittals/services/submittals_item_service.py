from uuid import UUID

from commons.db.v6.crm.submittals import (
    SubmittalItem,
    SubmittalItemApprovalStatus,
    SubmittalItemMatchStatus,
)
from loguru import logger
from strawberry import UNSET

from app.graphql.submittals.repositories.submittals_repository import (
    SubmittalItemsRepository,
    SubmittalsRepository,
)
from app.graphql.submittals.strawberry.submittal_item_input import SubmittalItemInput
from app.graphql.submittals.strawberry.update_submittal_item_input import (
    UpdateSubmittalItemInput,
)


class SubmittalsItemService:
    """Service for managing submittal items."""

    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        repository: SubmittalsRepository,
        items_repository: SubmittalItemsRepository,
    ) -> None:
        self.repository = repository
        self.items_repository = items_repository

    async def add_item(
        self, submittal_id: UUID, input_data: SubmittalItemInput
    ) -> SubmittalItem:
        """Add an item to a submittal."""
        item = input_data.to_orm_model()

        if item.spec_sheet_id and item.highlight_version_id:
            item.match_status = SubmittalItemMatchStatus.EXACT_MATCH
        elif item.spec_sheet_id:
            item.match_status = SubmittalItemMatchStatus.PARTIAL_MATCH
        else:
            item.match_status = SubmittalItemMatchStatus.NO_MATCH

        created = await self.repository.add_item(submittal_id, item)
        logger.info(f"Added item {created.id} to submittal {submittal_id}")
        item_with_relations = await self.items_repository.get_by_id_with_relations(
            created.id
        )
        return item_with_relations or created

    async def update_item(
        self, item_id: UUID, input_data: UpdateSubmittalItemInput
    ) -> SubmittalItem:
        """Update a submittal item."""
        item = await self.items_repository.get_by_id(item_id)
        if not item:
            raise ValueError(f"SubmittalItem with id {item_id} not found")

        if input_data.spec_sheet_id is not UNSET:
            item.spec_sheet_id = input_data.spec_sheet_id
        if input_data.highlight_version_id is not UNSET:
            item.highlight_version_id = input_data.highlight_version_id
        if input_data.part_number is not None:
            item.part_number = input_data.part_number
        if input_data.manufacturer is not None:
            item.manufacturer = input_data.manufacturer
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
        else:
            if item.spec_sheet_id and item.highlight_version_id:
                item.match_status = SubmittalItemMatchStatus.EXACT_MATCH
            elif item.spec_sheet_id:
                item.match_status = SubmittalItemMatchStatus.PARTIAL_MATCH
            else:
                item.match_status = SubmittalItemMatchStatus.NO_MATCH
        if input_data.notes is not None:
            item.notes = input_data.notes

        updated = await self.items_repository.update(item)
        logger.info(f"Updated submittal item {item_id}")
        item_with_relations = await self.items_repository.get_by_id_with_relations(
            updated.id
        )
        return item_with_relations or updated

    async def remove_item(self, item_id: UUID) -> bool:
        """Remove a submittal item."""
        result = await self.items_repository.delete(item_id)
        if result:
            logger.info(f"Removed submittal item {item_id}")
        return result
