"""GraphQL response type for Submittal."""

from datetime import datetime
from typing import TYPE_CHECKING, Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import Submittal

from app.core.db.adapters.dto import DTOMixin
from app.graphql.submittals.strawberry.enums import (
    SubmittalStatusGQL,
    TransmittalPurposeGQL,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse

if TYPE_CHECKING:
    from app.graphql.submittals.strawberry.submittal_item_response import (
        SubmittalItemResponse,
    )
    from app.graphql.submittals.strawberry.submittal_revision_response import (
        SubmittalRevisionResponse,
    )
    from app.graphql.submittals.strawberry.submittal_stakeholder_response import (
        SubmittalStakeholderResponse,
    )


@strawberry.type
class SubmittalResponse(DTOMixin[Submittal]):
    """Response type for Submittal."""

    _instance: strawberry.Private[Submittal]
    id: UUID
    submittal_number: str
    quote_id: UUID | None
    job_id: UUID | None
    status: SubmittalStatusGQL
    transmittal_purpose: TransmittalPurposeGQL | None
    description: str | None
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: Submittal) -> Self:
        """Convert ORM model to GraphQL response."""
        return cls(
            _instance=model,
            id=model.id,
            submittal_number=model.submittal_number,
            quote_id=model.quote_id,
            job_id=model.job_id,
            status=SubmittalStatusGQL(model.status.value),
            transmittal_purpose=(
                TransmittalPurposeGQL(model.transmittal_purpose.value)
                if model.transmittal_purpose
                else None
            ),
            description=model.description,
            created_at=model.created_at,
        )

    @strawberry.field
    def created_by(self) -> UserResponse:
        """Resolve created_by from the ORM instance."""
        return UserResponse.from_orm_model(self._instance.created_by)

    @strawberry.field
    def items(self) -> list["SubmittalItemResponse"]:
        """Resolve items from the ORM instance."""
        from app.graphql.submittals.strawberry.submittal_item_response import (
            SubmittalItemResponse,
        )

        return SubmittalItemResponse.from_orm_model_list(self._instance.items)

    @strawberry.field
    def stakeholders(self) -> list["SubmittalStakeholderResponse"]:
        """Resolve stakeholders from the ORM instance."""
        from app.graphql.submittals.strawberry.submittal_stakeholder_response import (
            SubmittalStakeholderResponse,
        )

        return SubmittalStakeholderResponse.from_orm_model_list(
            self._instance.stakeholders
        )

    @strawberry.field
    def revisions(self) -> list["SubmittalRevisionResponse"]:
        """Resolve revisions from the ORM instance."""
        from app.graphql.submittals.strawberry.submittal_revision_response import (
            SubmittalRevisionResponse,
        )

        return SubmittalRevisionResponse.from_orm_model_list(self._instance.revisions)
