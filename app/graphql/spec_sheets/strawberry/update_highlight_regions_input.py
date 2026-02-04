from uuid import UUID

import strawberry

from app.graphql.spec_sheets.strawberry.highlight_region_input import (
    HighlightRegionInput,
)


@strawberry.input
class UpdateHighlightRegionsInput:
    """Input for updating all regions in a highlight version."""

    version_id: UUID
    regions: list[HighlightRegionInput]
