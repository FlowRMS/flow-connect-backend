from datetime import datetime
from typing import Any, Self
from uuid import UUID

import strawberry
from sqlalchemy.engine.row import Row

from app.graphql.ai.models.enums import AIEntityType, FileType, ProcessingStatus


@strawberry.type(name="PendingDocumentLandingPage")
class PendingDocumentLandingPageResponse:
    pending_document_id: UUID
    document_id: UUID
    document_type: str
    entity_type: str | None
    ai_status: str
    file_status: str | None
    cluster_id: UUID | None
    cluster_name: str | None
    created_at: datetime

    @classmethod
    def from_row(cls, row: Row[Any]) -> Self:
        return cls(
            pending_document_id=row.pending_document_id,
            document_id=row.document_id,
            document_type=FileType(row.document_type).name,
            entity_type=AIEntityType(row.entity_type).name if row.entity_type else None,
            ai_status=ProcessingStatus(row.ai_status).name,
            file_status=row.status,
            cluster_id=row.cluster_id,
            cluster_name=row.cluster_name,
            created_at=row.created_at,
        )

    @classmethod
    def from_row_list(cls, rows: list[Row[Any]]) -> list[Self]:
        return [cls.from_row(row) for row in rows]
