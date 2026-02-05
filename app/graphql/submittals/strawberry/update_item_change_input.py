import strawberry
from commons.db.v6.crm.submittals import SubmittalItemChange

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import ItemChangeStatusGQL


@strawberry.input
class UpdateItemChangeInput(BaseInputGQL[SubmittalItemChange]):
    status: ItemChangeStatusGQL | None = None
    notes: list[str] | None = None
    page_references: list[int] | None = None
    resolved: bool | None = None
    fixture_type: str | None = None
    catalog_number: str | None = None
    manufacturer: str | None = None
