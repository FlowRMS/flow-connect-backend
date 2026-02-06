import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert

from app.core.db.transient_session import TenantSession
from app.graphql.pos.agreement.models.agreement import Agreement


class AgreementRepository:
    def __init__(self, session: TenantSession) -> None:
        self.session = session

    async def create(self, agreement: Agreement) -> Agreement:
        self.session.add(agreement)
        await self.session.flush([agreement])
        return agreement

    async def get_by_connected_org_id(
        self,
        connected_org_id: uuid.UUID,
    ) -> Agreement | None:
        stmt = select(Agreement).where(Agreement.connected_org_id == connected_org_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(self, agreement: Agreement) -> Agreement:
        stmt = (
            insert(Agreement)
            .values(
                id=agreement.id,
                connected_org_id=agreement.connected_org_id,
                s3_key=agreement.s3_key,
                file_name=agreement.file_name,
                file_size=agreement.file_size,
                file_sha=agreement.file_sha,
                created_by_id=agreement.created_by_id,
            )
            .on_conflict_do_update(
                constraint="uq_agreements_connected_org_id",
                set_={
                    "s3_key": agreement.s3_key,
                    "file_name": agreement.file_name,
                    "file_size": agreement.file_size,
                    "file_sha": agreement.file_sha,
                },
            )
            .returning(Agreement)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete(self, connected_org_id: uuid.UUID) -> bool:
        stmt = delete(Agreement).where(Agreement.connected_org_id == connected_org_id)
        result: Any = await self.session.execute(stmt)
        return result.rowcount > 0
