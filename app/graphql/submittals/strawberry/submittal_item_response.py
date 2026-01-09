"""GraphQL response type for SubmittalItem."""

from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalItem

from app.core.db.adapters.dto import DTOMixin
from app.graphql.spec_sheets.strawberry.spec_sheet_highlight_response import (
    SpecSheetHighlightVersionResponse,
)
from app.graphql.spec_sheets.strawberry.spec_sheet_response import SpecSheetResponse
from app.graphql.submittals.strawberry.enums import (
    SubmittalItemApprovalStatusGQL,
    SubmittalItemMatchStatusGQL,
)


@strawberry.type
class SubmittalItemResponse(DTOMixin[SubmittalItem]):
    """Response type for SubmittalItem."""

    _instance: strawberry.Private[SubmittalItem]
    id: UUID
    submittal_id: UUID
    item_number: int
    quote_detail_id: UUID | None
    spec_sheet_id: UUID | None
    highlight_version_id: UUID | None
    part_number: str | None
    description: str | None
    quantity: Decimal | None
    approval_status: SubmittalItemApprovalStatusGQL
    match_status: SubmittalItemMatchStatusGQL
    notes: str | None
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: SubmittalItem) -> Self:
        """Convert ORM model to GraphQL response."""
        return cls(
            _instance=model,
            id=model.id,
            submittal_id=model.submittal_id,
            item_number=model.item_number,
            quote_detail_id=model.quote_detail_id,
            spec_sheet_id=model.spec_sheet_id,
            highlight_version_id=model.highlight_version_id,
            part_number=model.part_number,
            description=model.description,
            quantity=model.quantity,
            approval_status=SubmittalItemApprovalStatusGQL(model.approval_status.value),
            match_status=SubmittalItemMatchStatusGQL(model.match_status.value),
            notes=model.notes,
            created_at=model.created_at,
        )

    @strawberry.field
    def spec_sheet(self) -> SpecSheetResponse | None:
        """Resolve spec_sheet from the ORM instance."""
        if self._instance.spec_sheet:
            return SpecSheetResponse.from_orm_model(self._instance.spec_sheet)
        return None

    @strawberry.field
    def highlight_version(self) -> SpecSheetHighlightVersionResponse | None:
        """Resolve highlight_version from the ORM instance."""
        if self._instance.highlight_version:
            return SpecSheetHighlightVersionResponse.from_orm_model(
                self._instance.highlight_version
            )
        return None
