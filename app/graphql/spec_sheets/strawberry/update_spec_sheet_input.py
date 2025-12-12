"""GraphQL input type for updating a SpecSheet."""

import strawberry

from app.core.strawberry.inputs import BaseInputGQL
from app.graphql.spec_sheets.models.spec_sheet_model import SpecSheet


@strawberry.input
class UpdateSpecSheetInput(BaseInputGQL[SpecSheet]):
    """Input for updating an existing spec sheet."""

    display_name: str | None = strawberry.UNSET
    categories: list[str] | None = strawberry.UNSET
    tags: list[str] | None = strawberry.UNSET
    folder_path: str | None = strawberry.UNSET
    needs_review: bool | None = strawberry.UNSET
    published: bool | None = strawberry.UNSET
