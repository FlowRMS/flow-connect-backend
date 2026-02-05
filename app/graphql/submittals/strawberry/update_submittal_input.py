from datetime import date

import strawberry
from commons.db.v6.crm.submittals import Submittal

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import (
    SubmittalStatusGQL,
    TransmittalPurposeGQL,
)
from app.graphql.submittals.strawberry.submittal_config_input import (
    SubmittalConfigInput,
)


@strawberry.input
class UpdateSubmittalInput(BaseInputGQL[Submittal]):
    status: SubmittalStatusGQL | None = strawberry.UNSET  # type: ignore[assignment]
    transmittal_purpose: TransmittalPurposeGQL | None = strawberry.UNSET  # type: ignore[assignment]
    description: str | None = strawberry.UNSET  # type: ignore[assignment]
    job_location: str | None = strawberry.UNSET  # type: ignore[assignment]
    bid_date: date | None = strawberry.UNSET  # type: ignore[assignment]
    tags: list[str] | None = strawberry.UNSET  # type: ignore[assignment]
    config: SubmittalConfigInput | None = strawberry.UNSET  # type: ignore[assignment]
