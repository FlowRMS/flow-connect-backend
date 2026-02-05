from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalItemChange

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import ItemChangeStatusGQL


@strawberry.input
class AddItemChangeInput(BaseInputGQL[SubmittalItemChange]):
    """Input for adding an item change to a change analysis."""

    change_analysis_id: UUID
    fixture_type: str
    catalog_number: str
    manufacturer: str
    item_id: UUID | None = None
    status: ItemChangeStatusGQL = ItemChangeStatusGQL.APPROVED
    notes: list[str] | None = None
    page_references: list[int] | None = None
