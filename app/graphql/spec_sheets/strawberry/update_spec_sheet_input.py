"""GraphQL input type for updating a SpecSheet."""

import strawberry
from commons.db.v6.crm.spec_sheets.spec_sheet_model import SpecSheet

from app.core.strawberry.inputs import BaseInputGQL


@strawberry.input
class UpdateSpecSheetInput(BaseInputGQL[SpecSheet]):
    """Input for updating an existing spec sheet.

    Note: To move a spec sheet to a different folder, use the
    moveSpecSheetToFolder mutation instead.
    """

    display_name: str | None = strawberry.UNSET
    categories: list[str] | None = strawberry.UNSET
    tags: list[str] | None = strawberry.UNSET
    needs_review: bool | None = strawberry.UNSET
    published: bool | None = strawberry.UNSET
