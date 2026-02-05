from decimal import Decimal
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import (
    SubmittalItem,
    SubmittalItemApprovalStatus,
    SubmittalItemMatchStatus,
)

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import (
    SubmittalItemApprovalStatusGQL,
    SubmittalItemMatchStatusGQL,
)


@strawberry.input
class SubmittalItemInput(BaseInputGQL[SubmittalItem]):
    item_number: int
    quote_detail_id: UUID | None = None
    spec_sheet_id: UUID | None = None
    highlight_version_id: UUID | None = None
    part_number: str | None = None
    manufacturer: str | None = None
    description: str | None = None
    quantity: Decimal | None = None
    approval_status: SubmittalItemApprovalStatusGQL = (
        SubmittalItemApprovalStatusGQL.PENDING
    )
    match_status: SubmittalItemMatchStatusGQL = SubmittalItemMatchStatusGQL.NO_MATCH
    notes: str | None = None
    lead_time: str | None = None

    def to_orm_model(self) -> SubmittalItem:
        return SubmittalItem(
            item_number=self.item_number,
            quote_detail_id=self.quote_detail_id,
            spec_sheet_id=self.spec_sheet_id,
            highlight_version_id=self.highlight_version_id,
            part_number=self.part_number,
            manufacturer=self.manufacturer,
            description=self.description,
            quantity=self.quantity,
            approval_status=SubmittalItemApprovalStatus(self.approval_status.value),
            match_status=SubmittalItemMatchStatus(self.match_status.value),
            notes=self.notes,
            lead_time=self.lead_time,
        )
