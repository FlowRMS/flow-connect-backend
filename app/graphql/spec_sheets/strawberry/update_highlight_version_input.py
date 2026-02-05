import strawberry


@strawberry.input
class UpdateHighlightVersionInput:
    """Input for updating an existing highlight version."""

    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
