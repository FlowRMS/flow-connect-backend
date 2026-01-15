"""GraphQL response type for SubmittalItem."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalItem

from app.core.db.adapters.dto import DTOMixin
from app.graphql.spec_sheets.strawberry.spec_sheet_highlight_response import (
    HighlightVersionResponse,
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
    quote_detail_id: Optional[UUID]
    spec_sheet_id: Optional[UUID]
    highlight_version_id: Optional[UUID]
    part_number: Optional[str]
    description: Optional[str]
    quantity: Optional[Decimal]
    approval_status: SubmittalItemApprovalStatusGQL
    match_status: SubmittalItemMatchStatusGQL
    notes: Optional[str]
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
    def spec_sheet(self) -> Optional[SpecSheetResponse]:
        """Resolve spec_sheet from the ORM instance."""
        if self._instance.spec_sheet:
            return SpecSheetResponse.from_orm_model(self._instance.spec_sheet)
        return None

    @strawberry.field
    def highlight_version(self) -> Optional[HighlightVersionResponse]:
        """Resolve highlight_version from the ORM instance."""
        if self._instance.highlight_version:
            return HighlightVersionResponse.from_orm_model(
                self._instance.highlight_version
            )
        return None
