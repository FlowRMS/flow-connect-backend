"""GraphQL input type for updating a SpecSheet."""

import strawberry


@strawberry.input
class UpdateSpecSheetInput:
    """Input for updating an existing spec sheet."""

    display_name: str | None = None
    categories: list[str] | None = None
    tags: list[str] | None = None
    folder_path: str | None = None
    needs_review: bool | None = None
    published: bool | None = None
