import uuid
from typing import Any

from sqlalchemy import select, update

from app.core.db.transient_session import TenantSession
from app.graphql.pos.data_exchange.models import ReceivedExchangeFile


class ReceivedExchangeFileRepository:
    def __init__(self, session: TenantSession) -> None:
        self.session = session

    async def create(self, file: ReceivedExchangeFile) -> ReceivedExchangeFile:
        self.session.add(file)
        await self.session.flush([file])
        return file

    async def list_for_org(
        self,
        org_id: uuid.UUID,
        *,
        period: str | None = None,
        senders: list[uuid.UUID] | None = None,
        is_pos: bool | None = None,
        is_pot: bool | None = None,
    ) -> list[ReceivedExchangeFile]:
        stmt = select(ReceivedExchangeFile).where(ReceivedExchangeFile.org_id == org_id)

        if period is not None:
            stmt = stmt.where(ReceivedExchangeFile.reporting_period == period)

        if senders is not None:
            stmt = stmt.where(ReceivedExchangeFile.sender_org_id.in_(senders))

        if is_pos is not None:
            stmt = stmt.where(ReceivedExchangeFile.is_pos == is_pos)

        if is_pot is not None:
            stmt = stmt.where(ReceivedExchangeFile.is_pot == is_pot)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(
        self,
        file_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> ReceivedExchangeFile | None:
        stmt = select(ReceivedExchangeFile).where(
            ReceivedExchangeFile.id == file_id,
            ReceivedExchangeFile.org_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(
        self,
        file_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str,
    ) -> bool:
        stmt = (
            update(ReceivedExchangeFile)
            .where(
                ReceivedExchangeFile.id == file_id,
                ReceivedExchangeFile.org_id == org_id,
            )
            .values(status=status)
        )
        result: Any = await self.session.execute(stmt)
        return result.rowcount > 0
