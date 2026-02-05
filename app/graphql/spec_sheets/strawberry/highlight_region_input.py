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
