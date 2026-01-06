import uuid

from commons.db.v6.crm.jobs import ConfirmedDifferentJob
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


class ConfirmedDifferentJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        super().__init__()
        self.session = session

    def _normalize_job_ids(
        self,
        job_id_1: uuid.UUID,
        job_id_2: uuid.UUID,
    ) -> tuple[uuid.UUID, uuid.UUID]:
        if job_id_1 < job_id_2:
            return job_id_1, job_id_2
        return job_id_2, job_id_1

    async def is_confirmed_different(
        self,
        job_id_1: uuid.UUID,
        job_id_2: uuid.UUID,
    ) -> bool:
        normalized_1, normalized_2 = self._normalize_job_ids(job_id_1, job_id_2)
        stmt = select(ConfirmedDifferentJob).where(
            ConfirmedDifferentJob.job_id_1 == normalized_1,
            ConfirmedDifferentJob.job_id_2 == normalized_2,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_confirmed_different_for_job(
        self,
        job_id: uuid.UUID,
    ) -> list[uuid.UUID]:
        stmt = select(ConfirmedDifferentJob).where(
            or_(
                ConfirmedDifferentJob.job_id_1 == job_id,
                ConfirmedDifferentJob.job_id_2 == job_id,
            )
        )
        result = await self.session.execute(stmt)
        records = list(result.scalars().all())

        other_job_ids: list[uuid.UUID] = []
        for record in records:
            if record.job_id_1 == job_id:
                other_job_ids.append(record.job_id_2)
            else:
                other_job_ids.append(record.job_id_1)
        return other_job_ids

    async def create(
        self,
        job_id_1: uuid.UUID,
        job_id_2: uuid.UUID,
        confirmed_by_id: uuid.UUID,
        reason: str | None = None,
    ) -> ConfirmedDifferentJob:
        normalized_1, normalized_2 = self._normalize_job_ids(job_id_1, job_id_2)

        record = ConfirmedDifferentJob(
            job_id_1=normalized_1,
            job_id_2=normalized_2,
            confirmed_by_id=confirmed_by_id,
            reason=reason,
        )
        self.session.add(record)
        await self.session.flush()
        return record

    async def delete(
        self,
        job_id_1: uuid.UUID,
        job_id_2: uuid.UUID,
    ) -> bool:
        normalized_1, normalized_2 = self._normalize_job_ids(job_id_1, job_id_2)
        stmt = select(ConfirmedDifferentJob).where(
            ConfirmedDifferentJob.job_id_1 == normalized_1,
            ConfirmedDifferentJob.job_id_2 == normalized_2,
        )
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        if record:
            await self.session.delete(record)
            await self.session.flush()
            return True
        return False

    async def filter_confirmed_different_pairs(
        self,
        job_id: uuid.UUID,
        candidate_ids: list[uuid.UUID],
    ) -> list[uuid.UUID]:
        if not candidate_ids:
            return []
        confirmed_different = await self.get_confirmed_different_for_job(job_id)
        confirmed_set = set(confirmed_different)
        return [cid for cid in candidate_ids if cid not in confirmed_set]
