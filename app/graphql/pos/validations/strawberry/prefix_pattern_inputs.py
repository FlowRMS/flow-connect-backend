import strawberry


@strawberry.input
class CreatePrefixPatternInput:
    name: str
    description: str | None = None
