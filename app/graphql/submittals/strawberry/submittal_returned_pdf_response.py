from __future__ import annotations

from datetime import date, datetime
from typing import Self
from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.submittals import SubmittalReturnedPdf
from sqlalchemy import inspect

from app.core.db.adapters.dto import DTOMixin
from app.graphql.inject import inject
from app.graphql.submittals.strawberry.submittal_stakeholder_response import (
    SubmittalStakeholderResponse,
)
from app.graphql.v2.core.users.strawberry.user_response import UserResponse
from app.graphql.v2.files.services.file_service import FileService


@strawberry.type
class SubmittalReturnedPdfResponse(DTOMixin[SubmittalReturnedPdf]):
    _instance: strawberry.Private[SubmittalReturnedPdf]
    _created_by_response: strawberry.Private[UserResponse | None]
    _returned_by_stakeholder_response: strawberry.Private[
        SubmittalStakeholderResponse | None
    ]
    _change_analysis_response: strawberry.Private[
        SubmittalChangeAnalysisResponse | None
    ]
    _stored_file_url: strawberry.Private[str]
    _file_id: strawberry.Private[UUID | None]
    id: UUID
    revision_id: UUID
    file_name: str
    file_size: int
    returned_by_stakeholder_id: UUID | None
    received_date: date | None
    notes: str | None
    created_at: datetime
    created_by_id: UUID | None

    @classmethod
    def from_orm_model(cls, model: SubmittalReturnedPdf) -> Self:
        state = inspect(model)

        created_by_response: UserResponse | None = None
        if "created_by" not in state.unloaded and model.created_by is not None:
            created_by_response = UserResponse.from_orm_model(model.created_by)

        returned_by_stakeholder_response: SubmittalStakeholderResponse | None = None
        if (
            "returned_by_stakeholder" not in state.unloaded
            and model.returned_by_stakeholder is not None
        ):
            returned_by_stakeholder_response = (
                SubmittalStakeholderResponse.from_orm_model(
                    model.returned_by_stakeholder
                )
            )

        change_analysis_response: SubmittalChangeAnalysisResponse | None = None
        if (
            "change_analysis" not in state.unloaded
            and model.change_analysis is not None
        ):
            change_analysis_response = SubmittalChangeAnalysisResponse.from_orm_model(
                model.change_analysis
            )

        return cls(
            _instance=model,
            _created_by_response=created_by_response,
            _returned_by_stakeholder_response=returned_by_stakeholder_response,
            _change_analysis_response=change_analysis_response,
            _stored_file_url=model.file_url,
            _file_id=model.file_id,
            id=model.id,
            revision_id=model.revision_id,
            file_name=model.file_name,
            file_size=model.file_size,
            returned_by_stakeholder_id=model.returned_by_stakeholder_id,
            received_date=model.received_date,
            notes=model.notes,
            created_at=model.created_at,
            created_by_id=model.created_by_id,
        )

    @strawberry.field
    @inject
    async def file_url(self, file_service: Injected[FileService]) -> str:
        """Generate a fresh presigned URL for the returned PDF file."""
        if self._file_id:
            try:
                presigned_url = await file_service.get_presigned_url(self._file_id)
                if presigned_url:
                    return presigned_url
            except Exception:
                pass
        return self._stored_file_url

    @strawberry.field
    def file_id(self) -> UUID | None:
        return self._file_id

    @strawberry.field
    def created_by(self) -> UserResponse | None:
        return self._created_by_response

    @strawberry.field
    def returned_by_stakeholder(self) -> SubmittalStakeholderResponse | None:
        return self._returned_by_stakeholder_response

    @strawberry.field
    def change_analysis(self) -> SubmittalChangeAnalysisResponse | None:
        return self._change_analysis_response


# Import here to avoid circular imports
from app.graphql.submittals.strawberry.submittal_change_analysis_response import (  # noqa: E402
    SubmittalChangeAnalysisResponse,
)
