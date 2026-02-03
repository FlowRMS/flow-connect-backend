from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalChangeAnalysis
from sqlalchemy import inspect

from app.core.db.adapters.dto import DTOMixin
from app.graphql.submittals.strawberry.enums import (
    ChangeAnalysisSourceGQL,
    OverallChangeStatusGQL,
)
from app.graphql.submittals.strawberry.submittal_item_change_response import (
    SubmittalItemChangeResponse,
)


@strawberry.type
class SubmittalChangeAnalysisResponse(DTOMixin[SubmittalChangeAnalysis]):
    _instance: strawberry.Private[SubmittalChangeAnalysis]
    _item_changes_response: strawberry.Private[list[SubmittalItemChangeResponse]]
    id: UUID
    returned_pdf_id: UUID
    analyzed_by: ChangeAnalysisSourceGQL
    overall_status: OverallChangeStatusGQL
    total_changes_detected: int
    summary: str | None
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: SubmittalChangeAnalysis) -> Self:
        state = inspect(model)

        # Extract item_changes
        item_changes_response: list[SubmittalItemChangeResponse] = []
        if "item_changes" not in state.unloaded and model.item_changes:
            item_changes_response = [
                SubmittalItemChangeResponse.from_orm_model(change)
                for change in model.item_changes
            ]

        return cls(
            _instance=model,
            _item_changes_response=item_changes_response,
            id=model.id,
            returned_pdf_id=model.returned_pdf_id,
            analyzed_by=ChangeAnalysisSourceGQL(model.analyzed_by.value),
            overall_status=OverallChangeStatusGQL(model.overall_status.value),
            total_changes_detected=model.total_changes_detected,
            summary=model.summary,
            created_at=model.created_at,
        )

    @strawberry.field
    def item_changes(self) -> list[SubmittalItemChangeResponse]:
        return self._item_changes_response
