import uuid

from commons.db.models.tenant import Tenant
from sqlalchemy import select

from app.core.db.base_session import TenantSession


class TenantsRepository:
    def __init__(self, base_session: TenantSession) -> None:
        super().__init__()
        self.session = base_session

    async def create(self, tenant: Tenant) -> Tenant:
        self.session.add(tenant)
        await self.session.flush([tenant])
        return tenant

    async def get_by_id(self, tenant_id: uuid.UUID) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_url(self, url: str) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.url == url)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Tenant]:
        stmt = select(Tenant).order_by(Tenant.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def url_exists(self, url: str) -> bool:
        stmt = select(Tenant.id).where(Tenant.url == url)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def database_exists(self, database: str) -> bool:
        stmt = select(Tenant.id).where(Tenant.database == database)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def update(self, tenant: Tenant) -> Tenant:
        _ = await self.session.merge(tenant)
        await self.session.flush([tenant])
        return tenant
