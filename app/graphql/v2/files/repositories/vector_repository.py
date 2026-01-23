from uuid import UUID

from commons.vector.vector_embedding_service import VectorEmbeddingService
from commons.vector.vector_service import VectorService
from loguru import logger
from qdrant_client.models import PointStruct

from app.core.context_wrapper import ContextWrapper

COLLECTION_NAME = "uploads-collection"


class VectorRepository:
    def __init__(
        self,
        vector_service: VectorService,
        vector_embedding_service: VectorEmbeddingService,
        context_wrapper: ContextWrapper,
    ):
        super().__init__()
        context = context_wrapper.get()
        auth_info = context.auth_info
        self.vector_service = vector_service
        self.vector_embedding_service = vector_embedding_service
        self.collection_name = COLLECTION_NAME
        self.auth_info = auth_info

    async def _insert_document(
        self,
        file_id: UUID,
        embedding: list[float],
        metadata: dict[str, str],
    ) -> None:
        point = PointStruct(
            id=str(file_id),
            vector=embedding,
            payload=metadata,
        )

        _ = await self.vector_service.client.upsert(
            collection_name=self.collection_name,
            points=[point],
        )
        logger.info(f"Inserted document {file_id} into vector store")

    async def insert_document(
        self,
        file_id: UUID,
        file_name: str,
        file_content: str,
        page_number: int | None = None,
    ) -> None:
        if file_content is None or len(file_content) == 0:
            logger.error(f"File content is empty for file {file_id} - {file_name} - {page_number}")
            return
        embedding = await self.vector_embedding_service.generate_embedding(file_content)
        if len(embedding) == 0:
            logger.error(f"Failed to generate embedding for file {file_id} - {file_name} - {page_number}")
            return
        await self._insert_document(
            file_id=file_id,
            embedding=embedding,
            metadata={
                "tenant_id": self.auth_info.tenant_name,
                "file_id": str(file_id),
                "file_name": file_name,
                "content": file_content,
                "page_number": str(page_number) if page_number is not None else "N/A",
            },
        )
