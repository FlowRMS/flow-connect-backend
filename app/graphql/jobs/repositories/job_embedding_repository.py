import uuid

from commons.db.v6.crm.jobs import JobEmbedding
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class JobEmbeddingRepository:
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    async def get_by_job_id(self, job_id: uuid.UUID) -> JobEmbedding | None:
        stmt = select(JobEmbedding).where(JobEmbedding.job_id == job_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_job_ids(
        self,
        job_ids: list[uuid.UUID],
    ) -> list[JobEmbedding]:
        if not job_ids:
            return []
        stmt = select(JobEmbedding).where(JobEmbedding.job_id.in_(job_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert(self, embedding: JobEmbedding) -> JobEmbedding:
        existing = await self.get_by_job_id(embedding.job_id)
        if existing:
            existing.embedding_version = embedding.embedding_version
            existing.text_hash = embedding.text_hash
            await self.session.flush()
            return existing
        self.session.add(embedding)
        await self.session.flush()
        return embedding

    async def delete_by_job_id(self, job_id: uuid.UUID) -> bool:
        embedding = await self.get_by_job_id(job_id)
        if embedding:
            await self.session.delete(embedding)
            await self.session.flush()
            return True
        return False

    async def get_jobs_without_embeddings(
        self,
        job_ids: list[uuid.UUID],
    ) -> list[uuid.UUID]:
        if not job_ids:
            return []
        existing = await self.get_by_job_ids(job_ids)
        existing_job_ids = {e.job_id for e in existing}
        return [jid for jid in job_ids if jid not in existing_job_ids]
