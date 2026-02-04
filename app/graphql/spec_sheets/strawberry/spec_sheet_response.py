from datetime import datetime
from typing import Self
from uuid import UUID

import strawberry
from aioinject import Injected
from commons.db.v6.crm.spec_sheets.spec_sheet_model import SpecSheet
from commons.s3.service import S3Service

from app.core.db.adapters.dto import DTOMixin
from app.graphql.inject import inject
from app.graphql.v2.core.users.strawberry.user_response import UserResponse


@strawberry.type
class SpecSheetResponse(DTOMixin[SpecSheet]):
    """Response type for SpecSheet."""

    _instance: strawberry.Private[SpecSheet]
    _file_path: strawberry.Private[str | None]  # S3 key from linked File
    _stored_file_url: strawberry.Private[str]  # Fallback URL from database
    id: UUID
    factory_id: UUID
    file_name: str
    display_name: str
    upload_source: str
    source_url: str | None
    file_size: int
    page_count: int
    categories: list[str]
    tags: list[str] | None
    folder_id: UUID | None  # pyfiles.folders ID (from File.folder_id)
    needs_review: bool
    published: bool
    usage_count: int
    highlight_count: int
    created_at: datetime

    @classmethod
    def from_orm_model(cls, model: SpecSheet) -> Self:
        """Convert ORM model to GraphQL response."""
        # Get folder_id and file_path from linked File if exists
        folder_id = model.file.folder_id if model.file else None
        file_path = model.file.file_path if model.file else None

        return cls(
            _instance=model,
            _file_path=file_path,
            _stored_file_url=model.file_url,
            id=model.id,
            factory_id=model.factory_id,
            file_name=model.file_name,
            display_name=model.display_name,
            upload_source=model.upload_source,
            source_url=model.source_url,
            file_size=model.file_size,
            page_count=model.page_count,
            categories=model.categories,
            tags=model.tags,
            folder_id=folder_id,
            needs_review=model.needs_review,
            published=model.published,
            usage_count=model.usage_count,
            highlight_count=model.highlight_count,
            created_at=model.created_at,
        )

    @strawberry.field
    @inject
    async def file_url(self, s3_service: Injected[S3Service]) -> str:
        """
        Generate a fresh presigned URL for the spec sheet file.

        This ensures the URL is always valid (not expired).
        """
        if self._file_path:
            try:
                return await s3_service.generate_presigned_url(
                    key=self._file_path,
                    expires_in=86400,  # 24 hours
                )
            except Exception:
                # Fall back to stored URL if presigned generation fails
                return self._stored_file_url
        return self._stored_file_url

    @strawberry.field
    def created_by(self) -> UserResponse:
        """Resolve created_by from the ORM instance."""
        return UserResponse.from_orm_model(self._instance.created_by)
