from datetime import UTC, datetime
from typing import Optional
from uuid import UUID

from commons.auth import AuthInfo
from commons.db.v6.fulfillment import FulfillmentDocument, FulfillmentDocumentType
from strawberry.file_uploads import Upload

from app.graphql.v2.core.fulfillment.repositories.fulfillment_document_repository import (
    FulfillmentDocumentRepository,
)
from app.graphql.v2.core.fulfillment.repositories.fulfillment_order_repository import (
    FulfillmentOrderRepository,
)
from app.graphql.v2.files.services.file_service import FileService
from app.graphql.v2.files.services.file_upload_service import FileUploadService


class FulfillmentDocumentService:
    def __init__(  # pyright: ignore[reportMissingSuperCall]
        self,
        document_repository: FulfillmentDocumentRepository,
        fulfillment_repository: FulfillmentOrderRepository,
        file_upload_service: FileUploadService,
        file_service: FileService,
        auth_info: AuthInfo,
    ):
        self.document_repository = document_repository
        self.fulfillment_repository = fulfillment_repository
        self.file_upload_service = file_upload_service
        self.file_service = file_service
        self.auth_info = auth_info

    async def add_document(
        self,
        fulfillment_order_id: UUID,
        document_type: FulfillmentDocumentType,
        file_name: str,
        file_url: str,
        file_size: int | None = None,
        mime_type: str | None = None,
        notes: str | None = None,
    ) -> FulfillmentDocument:
        """Add a document to a fulfillment order."""
        # Verify fulfillment order exists
        order = await self.fulfillment_repository.get_by_id(fulfillment_order_id)
        if not order:
            raise ValueError(f"Fulfillment order {fulfillment_order_id} not found")

        # Create document
        document = FulfillmentDocument(
            document_type=document_type,
            file_name=file_name,
            file_url=file_url,
            file_size=file_size,
            mime_type=mime_type,
            notes=notes,
            uploaded_at=datetime.now(UTC).replace(tzinfo=None),
        )
        document.fulfillment_order_id = fulfillment_order_id
        document.created_by_id = self.auth_info.flow_user_id

        return await self.document_repository.create(document)

    async def delete_document(self, document_id: UUID) -> bool:
        """Delete a document from a fulfillment order."""
        document = await self.document_repository.get_by_id(document_id)
        if not document:
            raise ValueError(f"Document {document_id} not found")

        # Delete the linked File record (which also deletes from S3)
        if document.file_id:
            _ = await self.file_service.delete_file(document.file_id)
        elif document.file_url:
            # Fallback for documents without linked File record
            s3_key = self.file_upload_service.extract_s3_key_from_path(
                document.file_url
            )
            if s3_key:
                await self.file_upload_service.delete_file(s3_key)

        _ = await self.document_repository.delete(document_id)
        return True

    async def upload_document(
        self,
        fulfillment_order_id: UUID,
        document_type: FulfillmentDocumentType,
        file: Upload,
        notes: Optional[str] = None,
    ) -> FulfillmentDocument:
        """Upload a file and create a document record for a fulfillment order."""
        # Verify fulfillment order exists
        order = await self.fulfillment_repository.get_by_id(fulfillment_order_id)
        if not order:
            raise ValueError(f"Fulfillment order {fulfillment_order_id} not found")

        # Upload file to S3 and create File record in pyfiles.files
        file_record = await self.file_service.upload_file(
            file_upload=file,
            file_name=file.filename,
            folder_path=f"fulfillment/{fulfillment_order_id}/documents",
        )

        # Get presigned URL for the file using the FileService
        presigned_url = await self.file_service.get_presigned_url(file_record.id)
        if not presigned_url:
            raise ValueError("Failed to generate presigned URL for uploaded file")

        # Create document record linked to the File
        document = FulfillmentDocument(
            document_type=document_type,
            file_name=file.filename,
            file_url=presigned_url,
            file_size=file_record.file_size,
            mime_type=file.content_type or "application/octet-stream",
            notes=notes,
            uploaded_at=datetime.now(UTC).replace(tzinfo=None),
        )
        document.fulfillment_order_id = fulfillment_order_id
        document.created_by_id = self.auth_info.flow_user_id
        document.file_id = file_record.id

        created = await self.document_repository.create(document)
        # Reload with relationships for GraphQL response
        return await self.document_repository.get_with_user(created.id)  # type: ignore

    async def get_documents_by_order(
        self, fulfillment_order_id: UUID
    ) -> list[FulfillmentDocument]:
        """Get all documents for a fulfillment order."""
        return await self.document_repository.find_by_fulfillment_order(
            fulfillment_order_id
        )
