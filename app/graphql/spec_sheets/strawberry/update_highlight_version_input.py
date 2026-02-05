import strawberry
from commons.db.v6.crm.spec_sheets.spec_sheet_highlight_model import (
    SpecSheetHighlightVersion,
)

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class UpdateHighlightVersionInput(BaseInputGQL[SpecSheetHighlightVersion]):
    name: str | None = strawberry.UNSET  # type: ignore[assignment]
    description: str | None = strawberry.UNSET  # type: ignore[assignment]
    is_active: bool | None = strawberry.UNSET  # type: ignore[assignment]
