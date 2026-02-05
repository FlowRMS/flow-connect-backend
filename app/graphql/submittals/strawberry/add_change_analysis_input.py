from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import (
    ChangeAnalysisSource,
    OverallChangeStatus,
    SubmittalChangeAnalysis,
)

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import (
    ChangeAnalysisSourceGQL,
    OverallChangeStatusGQL,
)
from app.graphql.submittals.strawberry.submittal_item_change_input import (
    SubmittalItemChangeInput,
)


@strawberry.input
class AddChangeAnalysisInput(BaseInputGQL[SubmittalChangeAnalysis]):
    returned_pdf_id: UUID
    analyzed_by: ChangeAnalysisSourceGQL = ChangeAnalysisSourceGQL.MANUAL
    overall_status: OverallChangeStatusGQL = OverallChangeStatusGQL.APPROVED
    summary: str | None = None
    item_changes: list[SubmittalItemChangeInput] | None = None

    def to_orm_model(self) -> SubmittalChangeAnalysis:
        item_changes = [change.to_orm_model() for change in (self.item_changes or [])]
        return SubmittalChangeAnalysis(
            analyzed_by=ChangeAnalysisSource(self.analyzed_by.value),
            overall_status=OverallChangeStatus(self.overall_status.value),
            summary=self.summary,
            total_changes_detected=len(item_changes),
            item_changes=item_changes,
        )
