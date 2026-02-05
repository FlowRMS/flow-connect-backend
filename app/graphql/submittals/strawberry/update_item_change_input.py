import strawberry
from commons.db.v6.crm.submittals import SubmittalItemChange

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.submittals.strawberry.enums import ItemChangeStatusGQL


@strawberry.input
class UpdateItemChangeInput(BaseInputGQL[SubmittalItemChange]):
    status: ItemChangeStatusGQL | None = strawberry.UNSET  # type: ignore[assignment]
    notes: list[str] | None = strawberry.UNSET  # type: ignore[assignment]
    page_references: list[int] | None = strawberry.UNSET  # type: ignore[assignment]
    resolved: bool | None = strawberry.UNSET  # type: ignore[assignment]
    fixture_type: str | None = strawberry.UNSET  # type: ignore[assignment]
    catalog_number: str | None = strawberry.UNSET  # type: ignore[assignment]
    manufacturer: str | None = strawberry.UNSET  # type: ignore[assignment]
