from datetime import date, datetime
from typing import Annotated, Self
from uuid import UUID

import strawberry
from commons.db.v6.crm.submittals import Submittal

from app.core.db.adapters.dto import DTOMixin
from app.graphql.submittals.strawberry.enums import (
    SubmittalStatusGQL,
    TransmittalPurposeGQL,
)
from app.graphql.submittals.strawberry.submittal_config_response import (
    SubmittalConfigResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class SubmittalResponse(DTOMixin[Submittal]):
    """Response type for Submittal."""

    _instance: strawberry.Private[Submittal]
    _created_by_response: strawberry.Private[UserResponse | None]
    id: UUID
    submittal_number: str
    quote_id: UUID | None
    job_id: UUID | None
    status: SubmittalStatusGQL
    transmittal_purpose: TransmittalPurposeGQL | None
    description: str | None
    job_location: str | None
    bid_date: date | None
    tags: list[str] | None
    created_at: datetime
    created_by_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: Submittal) -> Self:
        """Convert ORM model to GraphQL response."""
        from sqlalchemy.orm.attributes import instance_state

        # Try to extract created_by while session might still be active
        created_by_response: UserResponse | None = None
        state = instance_state(model)
        if "created_by" in state.dict and model.created_by is not None:
            # Relationship is already loaded
            created_by_response = UserResponse.from_orm_model(model.created_by)

        return cls(
            _instance=model,
            _created_by_response=created_by_response,
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
            job_location=model.job_location,
            bid_date=model.bid_date,
            tags=model.tags,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
        )

    @strawberry.field
    def created_by(self) -> UserResponse | None:
        """Resolve created_by from cached response."""
        return self._created_by_response

    @strawberry.field
    def items(
        self,
    ) -> list[
        Annotated[
            "SubmittalItemResponse",  # pyright: ignore[reportUndefinedVariable]
            strawberry.lazy(
                "app.graphql.submittals.strawberry.submittal_item_response"
            ),
        ]
    ]:
        """Resolve items from the ORM instance."""
        from app.graphql.submittals.strawberry.submittal_item_response import (
            SubmittalItemResponse,
        )

        return SubmittalItemResponse.from_orm_model_list(self._instance.items)

    @strawberry.field
    def stakeholders(
        self,
    ) -> list[
        Annotated[
            "SubmittalStakeholderResponse",  # pyright: ignore[reportUndefinedVariable]
            strawberry.lazy(
                "app.graphql.submittals.strawberry.submittal_stakeholder_response"
            ),
        ]
    ]:
        """Resolve stakeholders from the ORM instance."""
        from app.graphql.submittals.strawberry.submittal_stakeholder_response import (
            SubmittalStakeholderResponse,
        )

        return SubmittalStakeholderResponse.from_orm_model_list(
            self._instance.stakeholders
        )

    @strawberry.field
    def revisions(
        self,
    ) -> list[
        Annotated[
            "SubmittalRevisionResponse",  # pyright: ignore[reportUndefinedVariable]
            strawberry.lazy(
                "app.graphql.submittals.strawberry.submittal_revision_response"
            ),
        ]
    ]:
        """Resolve revisions from the ORM instance."""
        from app.graphql.submittals.strawberry.submittal_revision_response import (
            SubmittalRevisionResponse,
        )

        return SubmittalRevisionResponse.from_orm_model_list(self._instance.revisions)

    @strawberry.field
    def config(self) -> SubmittalConfigResponse:
        """Resolve config from the ORM instance."""
        return SubmittalConfigResponse.from_orm_model(self._instance)
