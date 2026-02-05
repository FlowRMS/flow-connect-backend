import strawberry
from commons.db.v6.crm.submittals import SubmittalChangeAnalysis

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import OverallChangeStatusGQL


@strawberry.input
class UpdateChangeAnalysisInput(BaseInputGQL[SubmittalChangeAnalysis]):
    overall_status: OverallChangeStatusGQL | None = strawberry.UNSET  # type: ignore[assignment]
    summary: str | None = strawberry.UNSET  # type: ignore[assignment]
