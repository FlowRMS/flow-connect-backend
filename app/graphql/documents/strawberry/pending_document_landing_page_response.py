from datetime import datetime
from typing import Any, Self
from uuid import UUID

import strawberry
from commons.db.v6.ai.documents.enums import (
    DocumentEntityType,
    FileType,
    ProcessingStatus,
)
from commons.db.v6.ai.documents.enums.workflow_status import WorkflowStatus
from sqlalchemy.engine.row import Row

from app.core.db.adapters.dto import LandingPageBase


@strawberry.type(name="PendingDocumentLandingPage")
class PendingDocumentLandingPageResponse(LandingPageBase):
    id: UUID
    created_at: datetime
    created_by: str
    created_by_id: UUID
    cluster_id: UUID | None
    cluster_name: str | None
    file_id: UUID
    file_name: str
    document_type: str
    entity_type: str | None
    status: str
    workflow_status: str | None
    is_new: bool

    @classmethod
    def from_orm_model(cls, row: Row[Any]) -> Self:
        data = cls.unpack_row(row)
        return cls(
            id=data["id"],
            created_at=data["created_at"],
            created_by=data["created_by"],
            created_by_id=data["created_by_id"],
            cluster_id=data["cluster_id"],
            cluster_name=data["cluster_name"],
            file_id=data["file_id"],
            file_name=data["file_name"],
            document_type=FileType(data["document_type"]).name,
            entity_type=(
                DocumentEntityType(data["entity_type"]).name
                if data["entity_type"] is not None
                else None
            ),
            workflow_status=(
                WorkflowStatus(data["workflow_status"]).name
                if data["workflow_status"] is not None
                else None
            ),
            status=ProcessingStatus(data["status"]).name,
            is_new=data["is_new"],
        )

    @classmethod
    def from_orm_model_list(cls, rows: list[Row[Any]]) -> list[Self]:
        return [cls.from_orm_model(row) for row in rows]
