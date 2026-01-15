"""GraphQL input types for SpecSheet Highlights."""

from uuid import UUID

import strawberry


@strawberry.input
class HighlightRegionInput:
    """Input for a single highlight region."""

    page_number: int
    x: float
    y: float
    width: float
    height: float
    shape_type: str  # 'rectangle', 'oval'
    color: str  # hex color like '#FFD700'
    annotation: str | None = None
    tags: list[str] | None = None


@strawberry.input
class CreateHighlightVersionInput:
    """Input for creating a new highlight version with regions."""

    spec_sheet_id: UUID
    name: str
    description: str | None = None
    regions: list[HighlightRegionInput]


@strawberry.input
class UpdateHighlightVersionInput:
    """Input for updating an existing highlight version."""

    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


@strawberry.input
class UpdateHighlightRegionsInput:
    """Input for updating all regions in a highlight version."""

    version_id: UUID
    regions: list[HighlightRegionInput]
