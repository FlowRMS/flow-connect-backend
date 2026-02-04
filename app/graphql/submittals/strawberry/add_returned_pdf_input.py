from datetime import date
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalReturnedPdf

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class AddReturnedPdfInput(BaseInputGQL[SubmittalReturnedPdf]):
    revision_id: UUID
    file_name: str
    file_url: str
    file_size: int = 0
    file_id: UUID | None = None
    returned_by_stakeholder_id: UUID | None = None
    received_date: date | None = None
    notes: str | None = None

    def to_orm_model(self) -> SubmittalReturnedPdf:
        return SubmittalReturnedPdf(
            file_name=self.file_name,
            file_url=self.file_url,
            file_size=self.file_size,
            file_id=self.file_id,
            returned_by_stakeholder_id=self.returned_by_stakeholder_id,
            received_date=self.received_date,
            notes=self.notes,
        )
