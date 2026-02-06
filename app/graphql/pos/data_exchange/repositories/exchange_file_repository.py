import uuid
from typing import Any

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import joinedload

from app.core.db.transient_session import TenantSession
from app.graphql.pos.data_exchange.models import (
    ExchangeFile,
    ExchangeFileStatus,
    ExchangeFileTargetOrg,
)


class ExchangeFileRepository:
    def __init__(self, session: TenantSession) -> None:
        self.session = session

    async def create(self, file: ExchangeFile) -> ExchangeFile:
        self.session.add(file)
        await self.session.flush([file])
        return file

    async def update(self, file: ExchangeFile) -> ExchangeFile:
        await self.session.flush([file])
        return file

    async def get_by_id(
        self,
        file_id: uuid.UUID,
        *,
        load_targets: bool = True,
    ) -> ExchangeFile | None:
        stmt = select(ExchangeFile).where(ExchangeFile.id == file_id)
        if load_targets:
            stmt = stmt.options(joinedload(ExchangeFile.target_organizations))
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def list_pending_for_org(self, org_id: uuid.UUID) -> list[ExchangeFile]:
        stmt = (
            select(ExchangeFile)
            .where(
                ExchangeFile.org_id == org_id,
                ExchangeFile.status == ExchangeFileStatus.PENDING.value,
            )
            .options(joinedload(ExchangeFile.target_organizations))
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def has_pending_with_sha_and_target(
        self,
        org_id: uuid.UUID,
        file_sha: str,
        target_org_ids: list[uuid.UUID],
    ) -> bool:
        stmt = (
            select(func.count())
            .select_from(ExchangeFile)
            .join(ExchangeFileTargetOrg)
            .where(
                ExchangeFile.org_id == org_id,
                ExchangeFile.file_sha == file_sha,
                ExchangeFile.status == ExchangeFileStatus.PENDING.value,
                ExchangeFileTargetOrg.connected_org_id.in_(target_org_ids),
            )
        )
        result = await self.session.execute(stmt)
        count = result.scalar_one_or_none()
        return count is not None and count > 0

    async def delete(self, file_id: uuid.UUID) -> bool:
        stmt = delete(ExchangeFile).where(ExchangeFile.id == file_id)
        result: Any = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_pending_stats(self, org_id: uuid.UUID) -> tuple[int, int]:
        stmt = select(
            func.count(ExchangeFile.id),
            func.coalesce(func.sum(ExchangeFile.row_count), 0),
        ).where(
            ExchangeFile.org_id == org_id,
            ExchangeFile.status == ExchangeFileStatus.PENDING.value,
        )
        result = await self.session.execute(stmt)
        row = result.one_or_none()
        if row is None:
            return 0, 0
        return row[0] or 0, row[1] or 0

    async def list_sent_files(
        self,
        org_id: uuid.UUID,
        *,
        period: str | None = None,
        organizations: list[uuid.UUID] | None = None,
        is_pos: bool | None = None,
        is_pot: bool | None = None,
    ) -> list[ExchangeFile]:
        stmt = (
            select(ExchangeFile)
            .where(
                ExchangeFile.org_id == org_id,
                ExchangeFile.status == ExchangeFileStatus.SENT.value,
            )
            .options(joinedload(ExchangeFile.target_organizations))
        )

        if period is not None:
            stmt = stmt.where(ExchangeFile.reporting_period == period)

        if organizations is not None:
            stmt = stmt.join(ExchangeFileTargetOrg).where(
                ExchangeFileTargetOrg.connected_org_id.in_(organizations)
            )

        if is_pos is not None:
            stmt = stmt.where(ExchangeFile.is_pos == is_pos)

        if is_pot is not None:
            stmt = stmt.where(ExchangeFile.is_pot == is_pot)

        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_last_sent_file(self, org_id: uuid.UUID) -> ExchangeFile | None:
        stmt = (
            select(ExchangeFile)
            .where(
                ExchangeFile.org_id == org_id,
                ExchangeFile.status == ExchangeFileStatus.SENT.value,
            )
            .order_by(ExchangeFile.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_pending_to_sent(self, org_id: uuid.UUID) -> int:
        stmt = (
            update(ExchangeFile)
            .where(
                ExchangeFile.org_id == org_id,
                ExchangeFile.status == ExchangeFileStatus.PENDING.value,
            )
            .values(status=ExchangeFileStatus.SENT.value)
        )
        result: Any = await self.session.execute(stmt)
        return result.rowcount
