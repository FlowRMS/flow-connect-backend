import contextlib
from collections.abc import AsyncIterator, Iterable
from typing import Any

import aioinject
from commons.db.controller import MultiTenantController
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.tenants.repositories.tenants_repository import TenantsRepository
from app.admin.tenants.services.tenant_creation_service import TenantCreationService
from app.admin.tenants.services.tenant_database_service import TenantDatabaseService
from app.admin.tenants.services.tenant_migration_service import TenantMigrationService


@contextlib.asynccontextmanager
async def create_base_session(
    controller: MultiTenantController,
) -> AsyncIterator[AsyncSession]:
    async with controller.base_scoped_session() as session:
        async with session.begin():
            yield session  # type: ignore[misc]


admin_providers: Iterable[aioinject.Provider[Any]] = [
    aioinject.Scoped(create_base_session),
    aioinject.Scoped(TenantsRepository),
    aioinject.Scoped(TenantDatabaseService),
    aioinject.Scoped(TenantMigrationService),
    aioinject.Scoped(TenantCreationService),
]
