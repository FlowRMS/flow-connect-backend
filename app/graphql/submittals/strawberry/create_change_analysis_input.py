from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalChangeAnalysis

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import (
    ChangeAnalysisSourceGQL,
    OverallChangeStatusGQL,
)


@strawberry.input
class CreateChangeAnalysisInput(BaseInputGQL[SubmittalChangeAnalysis]):
    """Input for creating a change analysis."""

    returned_pdf_id: UUID
    analyzed_by: ChangeAnalysisSourceGQL = ChangeAnalysisSourceGQL.MANUAL
    overall_status: OverallChangeStatusGQL = OverallChangeStatusGQL.APPROVED
    summary: str | None = None
