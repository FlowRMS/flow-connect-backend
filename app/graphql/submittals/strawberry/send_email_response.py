from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import SubmittalEmail

from app.core.db.adapters.dto import DTOMixin
from app.graphql.submittals.services.types import SendSubmittalEmailResult


@strawberry.type
class SubmittalEmailResponse(DTOMixin[SubmittalEmail]):
    """Response type for a recorded submittal email."""

    id: UUID
    submittal_id: UUID
    revision_id: UUID | None
    subject: str
    body: str | None
    recipient_emails: list[str]
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: SubmittalEmail) -> Self:
        """Convert ORM model to GraphQL response."""
        return cls(
            id=model.id,
            submittal_id=model.submittal_id,
            revision_id=model.revision_id,
            subject=model.subject,
            body=model.body,
            recipient_emails=model.recipient_emails or [],
            created_at=model.created_at,
        )


@strawberry.type
class SendSubmittalEmailResponse(DTOMixin[SubmittalEmail]):
    """Response type for send submittal email mutation."""

    success: bool
    error: str | None = None
    email: SubmittalEmailResponse | None = None
    provider: str | None = None

    @classmethod
    def from_orm_model(cls, model: SubmittalEmail) -> Self:
        """Create response from ORM model."""
        return cls(
            success=True,
            email=SubmittalEmailResponse.from_orm_model(model),
        )

    @classmethod
    def from_result(cls, result: SendSubmittalEmailResult) -> Self:
        """Convert service result to GraphQL response."""
        email_response = None
        if result.email_record:
            email_response = SubmittalEmailResponse.from_orm_model(result.email_record)

        provider_name = None
        if result.send_result and result.send_result.provider:
            provider_name = result.send_result.provider.name

        return cls(
            success=result.success,
            error=result.error,
            email=email_response,
            provider=provider_name,
        )
