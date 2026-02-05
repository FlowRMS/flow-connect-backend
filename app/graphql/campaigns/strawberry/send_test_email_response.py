import strawberry


@strawberry.type
class SendTestEmailResponse:
    success: bool
    error: str | None = None
