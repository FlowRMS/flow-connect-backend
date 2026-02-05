import strawberry
from commons.db.v6.crm.submittals import SubmittalChangeAnalysis

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import OverallChangeStatusGQL


@strawberry.input
class UpdateChangeAnalysisInput(BaseInputGQL[SubmittalChangeAnalysis]):
    """Input for updating a change analysis."""

    overall_status: OverallChangeStatusGQL | None = None
    summary: str | None = None
