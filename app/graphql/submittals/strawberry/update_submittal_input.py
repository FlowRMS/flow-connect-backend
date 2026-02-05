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
    status: SubmittalStatusGQL | None = None
    transmittal_purpose: TransmittalPurposeGQL | None = None
    description: str | None = None
    job_location: str | None = None
    bid_date: date | None = None
    tags: list[str] | None = None
    config: SubmittalConfigInput | None = None
