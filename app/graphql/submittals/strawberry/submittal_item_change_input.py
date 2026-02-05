from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import ItemChangeStatus, SubmittalItemChange

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import ItemChangeStatusGQL


@strawberry.input
class SubmittalItemChangeInput(BaseInputGQL[SubmittalItemChange]):
    item_id: UUID | None = None
    fixture_type: str
    catalog_number: str
    manufacturer: str
    status: ItemChangeStatusGQL = ItemChangeStatusGQL.APPROVED
    notes: list[str] | None = None
    page_references: list[int] | None = None

    def to_orm_model(self) -> SubmittalItemChange:
        return SubmittalItemChange(
            item_id=self.item_id,
            fixture_type=self.fixture_type,
            catalog_number=self.catalog_number,
            manufacturer=self.manufacturer,
            status=ItemChangeStatus(self.status.value),
            notes=self.notes,
            page_references=self.page_references,
        )
