from collections.abc import Iterable
from typing import Any

import aioinject
from commons.vector.vector_embedding_service import VectorEmbeddingService
from commons.vector.vector_service import VectorService

from app.core.config.vector_settings import VectorSettings


def create_vector_embedding_service(settings: VectorSettings) -> VectorEmbeddingService:
    return VectorEmbeddingService(api_key=settings.voyage_api_key)


def create_vector_service(settings: VectorSettings) -> VectorService:
    return VectorService(
        vector_url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        prefer_grpc=True,
    )


providers: Iterable[aioinject.Provider[Any]] = [
    aioinject.Singleton(create_vector_embedding_service),
    aioinject.Singleton(create_vector_service),
]
