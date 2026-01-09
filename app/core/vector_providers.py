from collections.abc import Iterable
from typing import Any
import aiohttp
import aioinject

from commons.utils.pdf_extractor.pdf import PDFExtractor
from commons.vector.vector_embedding_service import VectorEmbeddingService
from commons.vector.vector_service import VectorService
from qdrant_client.models import (
    PayloadSchemaType,
)
from app.core.config.vector_settings import VectorSettings
from app.graphql.v2.files.repositories.vector_repository import COLLECTION_NAME, VectorRepository

indexes = [
    ("tenant_id", PayloadSchemaType.KEYWORD),
]


async def create_vector_service(settings: VectorSettings) -> VectorService:
    service = VectorService(settings.vector_url, settings.vector_api_key)
    await service.create_collection_if_not_exists(
        collection_name=COLLECTION_NAME,
    )
    await service.register_indexes(
        collection_name=COLLECTION_NAME,
        indexes=indexes,
    )
    return service


def create_vector_embedding_service(settings: VectorSettings) -> VectorEmbeddingService:
    service = VectorEmbeddingService(settings.voyage_api_key)
    return service

def create_pdf_extractor(aiohttp_session: aiohttp.ClientSession) -> PDFExtractor:
    return PDFExtractor(aiohttp_session=aiohttp_session)


providers: Iterable[aioinject.Provider[Any]] = [
    aioinject.Singleton(create_vector_service),
    aioinject.Singleton(create_vector_embedding_service),
    aioinject.Scoped(VectorRepository),
    aioinject.Scoped(PDFExtractor),
]
