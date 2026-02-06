import uuid

from commons.db.models.tenant import Tenant
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class TenantRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_org_id(self, org_id: str) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.org_id == org_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_url(self, url: str) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.url == url)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, tenant: Tenant) -> Tenant:
        self.session.add(tenant)
        await self.session.flush([tenant])
        return tenant

    async def update_initialize(
        self,
        tenant_id: uuid.UUID,
        initialize: bool,
        alembic_version: str | None = None,
    ) -> None:
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await self.session.execute(stmt)
        tenant = result.scalar_one_or_none()
        if tenant:
            tenant.initialize = initialize
            if alembic_version is not None:
                tenant.alembic_version = alembic_version
            await self.session.flush([tenant])
