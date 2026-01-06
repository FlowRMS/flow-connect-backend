import hashlib
import uuid

from commons.auth import AuthInfo
from commons.db.v6.crm.jobs import Job, JobEmbedding
from commons.vector.vector_embedding_service import VectorEmbeddingService
from commons.vector.vector_service import VectorService
from loguru import logger
from qdrant_client.models import PointStruct

from app.core.config.vector_settings import VectorSettings
from app.graphql.jobs.repositories.job_embedding_repository import (
    JobEmbeddingRepository,
)

EMBEDDING_VERSION = "voyage-3-v1"


class JobEmbeddingService:
    def __init__(
        self,
        embedding_service: VectorEmbeddingService,
        vector_service: VectorService,
        repository: JobEmbeddingRepository,
        settings: VectorSettings,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.repository = repository
        self.settings = settings
        self.auth_info = auth_info
        self._collection_verified = False

    def _get_collection_name(self) -> str:
        return f"{self.settings.job_embeddings_collection}_{self.auth_info.tenant_id}"

    def _build_job_text(self, job: Job) -> str:
        parts: list[str] = []
        if job.job_name:
            parts.append(f"Job Name: {job.job_name}")
        if job.description:
            parts.append(f"Description: {job.description}")
        if job.structural_details:
            parts.append(f"Structural Details: {job.structural_details}")
        if job.structural_information:
            parts.append(f"Structural Information: {job.structural_information}")
        if job.additional_information:
            parts.append(f"Additional Information: {job.additional_information}")
        if job.job_type:
            parts.append(f"Job Type: {job.job_type}")
        return "\n".join(parts)

    def _compute_text_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    async def needs_update(self, job: Job) -> bool:
        existing = await self.repository.get_by_job_id(job.id)
        if not existing:
            return True
        job_text = self._build_job_text(job)
        current_hash = self._compute_text_hash(job_text)
        return existing.text_hash != current_hash

    async def generate_embedding(self, job: Job) -> list[float]:
        job_text = self._build_job_text(job)
        return await self.embedding_service.generate_embedding(job_text)

    async def ensure_collection_exists(self) -> None:
        if self._collection_verified:
            return
        collection_name = self._get_collection_name()
        await self.vector_service.create_collection_if_not_exists(collection_name)
        self._collection_verified = True

    async def get_stored_embedding(self, job_id: uuid.UUID) -> list[float] | None:
        collection_name = self._get_collection_name()
        try:
            results = await self.vector_service.client.retrieve(
                collection_name=collection_name,
                ids=[str(job_id)],
                with_vectors=True,
            )
            if results and len(results) > 0:
                point = results[0]
                if point.vector and isinstance(point.vector, list):
                    vector: list[float] = []
                    for x in point.vector:
                        if isinstance(x, (int, float)):
                            vector.append(float(x))
                    if vector:
                        return vector
        except Exception:
            pass
        return None

    async def upsert_job_embedding(self, job: Job) -> JobEmbedding:
        await self.ensure_collection_exists()

        job_text = self._build_job_text(job)
        text_hash = self._compute_text_hash(job_text)
        embedding = await self.embedding_service.generate_embedding(job_text)

        collection_name = self._get_collection_name()
        point = PointStruct(
            id=str(job.id),
            vector=embedding,
            payload={
                "job_id": str(job.id),
                "tenant_id": self.auth_info.tenant_id,
                "embedding_version": EMBEDDING_VERSION,
            },
        )
        _ = await self.vector_service.client.upsert(
            collection_name=collection_name,
            points=[point],
        )

        job_embedding = JobEmbedding(
            job_id=job.id,
            embedding_version=EMBEDDING_VERSION,
            text_hash=text_hash,
        )
        return await self.repository.upsert(job_embedding)

    async def upsert_job_embeddings_batch(
        self,
        jobs: list[Job],
        batch_size: int = 100,
    ) -> int:
        if not jobs:
            return 0

        await self.ensure_collection_exists()
        collection_name = self._get_collection_name()
        total_created = 0

        for i in range(0, len(jobs), batch_size):
            batch = jobs[i : i + batch_size]
            texts = [self._build_job_text(job) for job in batch]
            hashes = [self._compute_text_hash(text) for text in texts]

            embeddings = await self.embedding_service.generate_embeddings(texts)

            points = [
                PointStruct(
                    id=str(job.id),
                    vector=embedding,
                    payload={
                        "job_id": str(job.id),
                        "tenant_id": self.auth_info.tenant_id,
                        "embedding_version": EMBEDDING_VERSION,
                    },
                )
                for job, embedding in zip(batch, embeddings, strict=True)
            ]
            _ = await self.vector_service.client.upsert(
                collection_name=collection_name,
                points=points,
            )

            for job, text_hash in zip(batch, hashes, strict=True):
                job_embedding = JobEmbedding(
                    job_id=job.id,
                    embedding_version=EMBEDDING_VERSION,
                    text_hash=text_hash,
                )
                _ = await self.repository.upsert(job_embedding)

            total_created += len(batch)
            logger.info(f"Batch embedding: {total_created}/{len(jobs)} jobs processed")

        return total_created

    async def delete_job_embedding(self, job_id: uuid.UUID) -> bool:
        collection_name = self._get_collection_name()
        _ = await self.vector_service.client.delete(
            collection_name=collection_name,
            points_selector=[str(job_id)],
        )
        return await self.repository.delete_by_job_id(job_id)

    async def search_similar(
        self,
        job: Job,
        limit: int = 10,
        threshold: float | None = None,
    ) -> list[tuple[uuid.UUID, float]]:
        if threshold is None:
            threshold = self.settings.duplicate_threshold

        await self.ensure_collection_exists()
        collection_name = self._get_collection_name()

        embedding = await self.get_stored_embedding(job.id)
        if embedding is None:
            embedding = await self.generate_embedding(job)

        results = await self.vector_service.client.query_points(
            collection_name=collection_name,
            query=embedding,
            limit=limit + 1,
            score_threshold=threshold,
        )

        similar_jobs: list[tuple[uuid.UUID, float]] = []
        for point in results.points:
            point_job_id = uuid.UUID(str(point.id))
            if point_job_id != job.id:
                similar_jobs.append((point_job_id, point.score))

        return similar_jobs[:limit]
