import strawberry


@strawberry.type
class SendBatchResultResponse:
    emails_sent: int
    emails_failed: int
    emails_remaining: int
    is_completed: bool
    errors: list[str]

    @strawberry.field
    def success(self) -> bool:
        return self.emails_sent > 0 or self.is_completed
