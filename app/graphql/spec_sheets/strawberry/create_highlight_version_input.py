from uuid import UUID

import strawberry

from app.graphql.spec_sheets.strawberry.highlight_region_input import (
    HighlightRegionInput,
)


@strawberry.input
class CreateHighlightVersionInput:
    """Input for creating a new highlight version with regions."""

    spec_sheet_id: UUID
    name: str
    description: str | None = None
    regions: list[HighlightRegionInput]
