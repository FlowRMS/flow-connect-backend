from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalItem
from sqlalchemy import inspect

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
    quote_detail_id: UUID | None
    spec_sheet_id: UUID | None
    highlight_version_id: UUID | None
    part_number: str | None
    manufacturer: str | None
    description: str | None
    quantity: Decimal | None
    approval_status: SubmittalItemApprovalStatusGQL
    match_status: SubmittalItemMatchStatusGQL
    notes: str | None
    lead_time: str | None
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
            manufacturer=model.manufacturer,
            description=model.description,
            quantity=model.quantity,
            approval_status=SubmittalItemApprovalStatusGQL(model.approval_status.value),
            match_status=SubmittalItemMatchStatusGQL(model.match_status.value),
            notes=model.notes,
            lead_time=model.lead_time,
            created_at=model.created_at,
        )

    def _is_relationship_loaded(self, attr_name: str) -> bool:
        """Check if a relationship is loaded without triggering lazy load."""
        state = inspect(self._instance)
        return attr_name not in state.unloaded

    @strawberry.field
    def spec_sheet(self) -> SpecSheetResponse | None:
        """Resolve spec_sheet from the ORM instance."""
        if not self._is_relationship_loaded("spec_sheet"):
            return None
        if self._instance.spec_sheet:
            return SpecSheetResponse.from_orm_model(self._instance.spec_sheet)
        return None

    @strawberry.field
    def highlight_version(self) -> HighlightVersionResponse | None:
        """Resolve highlight_version from the ORM instance."""
        if not self._is_relationship_loaded("highlight_version"):
            return None
        if self._instance.highlight_version:
            return HighlightVersionResponse.from_orm_model(
                self._instance.highlight_version
            )
        return None
