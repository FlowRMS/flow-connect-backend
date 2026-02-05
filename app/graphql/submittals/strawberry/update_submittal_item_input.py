from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalItem
from strawberry import UNSET

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import (
    SubmittalItemApprovalStatusGQL,
    SubmittalItemMatchStatusGQL,
)


@strawberry.input
class UpdateSubmittalItemInput(BaseInputGQL[SubmittalItem]):
    # Use UNSET to distinguish "not provided" from "null"
    spec_sheet_id: UUID | None = UNSET  # type: ignore[assignment]
    highlight_version_id: UUID | None = UNSET  # type: ignore[assignment]
    part_number: str | None = None
    manufacturer: str | None = None
    description: str | None = None
    quantity: Decimal | None = None
    approval_status: SubmittalItemApprovalStatusGQL | None = None
    match_status: SubmittalItemMatchStatusGQL | None = None
    notes: str | None = None
    lead_time: str | None = None
