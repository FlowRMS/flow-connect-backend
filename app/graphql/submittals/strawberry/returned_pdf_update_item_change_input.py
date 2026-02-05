import strawberry
from commons.db.v6.crm.submittals import SubmittalItemChange

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import ItemChangeStatusGQL


@strawberry.input
class UpdateItemChangeInput(BaseInputGQL[SubmittalItemChange]):
    """Input for updating an item change."""

    status: ItemChangeStatusGQL | None = None
    notes: list[str] | None = None
    page_references: list[int] | None = None
    resolved: bool | None = None
