import re
import uuid
from dataclasses import dataclass

from commons.db.models.tenant import Tenant
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from commons.db.v6.user.user import User
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.admin.config.admin_settings import AdminSettings
from app.admin.tenants.repositories.tenants_repository import TenantsRepository
from app.admin.tenants.services.tenant_database_service import TenantDatabaseService
from app.admin.tenants.services.tenant_migration_service import TenantMigrationService
from app.auth.models import AuthUserInput
from app.auth.workos_auth_service import WorkOSAuthService
from app.core.config.settings import Settings


@dataclass
class TenantCreationResult:
    tenant: Tenant
    owner_workos_id: str
    workos_org_id: str
    success: bool
    message: str | None = None


class TenantCreationService:
    def __init__(
        self,
        repository: TenantsRepository,
        database_service: TenantDatabaseService,
        migration_service: TenantMigrationService,
        workos_service: WorkOSAuthService,
        admin_settings: AdminSettings,
        settings: Settings,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.database_service = database_service
        self.migration_service = migration_service
        self.workos_service = workos_service
        self.admin_settings = admin_settings
        self.settings = settings

    def _generate_url_slug(self, name: str) -> str:
        slug = name.lower().strip()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")

    async def _create_user_in_tenant_db(
        self,
        database_url: str,
        email: str,
        workos_user_id: str,
        role: RbacRoleEnum,
        first_name: str | None = None,
        last_name: str | None = None,
        external_id: uuid.UUID | None = None,
    ) -> uuid.UUID:
        engine = create_async_engine(database_url)
        try:
            async with AsyncSession(engine) as session:
                async with session.begin():
                    existing_user = await session.execute(
                        select(User).where(User.auth_provider_id == workos_user_id)
                    )
                    existing_user = existing_user.scalar_one_or_none()
                    if existing_user:
                        logger.info(f"User {email} already exists in tenant database")
                        return existing_user.id

                    user = User(
                        username=email,
                        first_name=first_name or email.split("@")[0],
                        last_name=last_name or "",
                        email=email,
                        role=role,
                        enabled=True,
                    )
                    user.auth_provider_id = workos_user_id
                    if external_id:
                        user.id = external_id
                    session.add(user)
                    logger.info(f"Created user {email} in tenant database")
                    return user.id
        finally:
            await engine.dispose()

    async def create_tenant(self, name: str, owner_email: str) -> TenantCreationResult:
        url_slug = self._generate_url_slug(name)

        if await self.repository.url_exists(url_slug):
            raise ValueError(f"Tenant with URL '{url_slug}' already exists")

        if await self.repository.database_exists(url_slug):
            raise ValueError(f"Database '{url_slug}' already exists")

        logger.info(f"Creating tenant: {name} (url: {url_slug}, db: {url_slug})")

        workos_org = await self.workos_service.create_tenant(name)
        if not workos_org:
            raise RuntimeError("Failed to create WorkOS organization")
        logger.info(f"Created WorkOS organization: {workos_org.id}")

        await self.database_service.setup_tenant_database(url_slug)
        logger.info(f"Created database and user: {url_slug}")

        alembic_version = await self.migration_service.run_migrations(url_slug)
        logger.info(f"Ran migrations, version: {alembic_version}")

        host = self.settings.pg_url.hosts()[0]
        db_host = host["host"]

        tenant = Tenant(
            id=uuid.uuid4(),
            initialize=True,
            name=name,
            url=url_slug,
            database=db_host,
            read_only_database=db_host,
            username=host["username"],
            alembic_version=alembic_version,
        )
        _ = await self.repository.create(tenant)
        logger.info(f"Created tenant record: {tenant.id}")

        database_url = (
            self.settings.pg_url.unicode_string().rsplit("/", 1)[0] + f"/{url_slug}"
        )
        owner_user_id = uuid.uuid4()
        owner_auth = await self.workos_service.create_user(
            AuthUserInput(
                email=owner_email,
                tenant_id=workos_org.id,
                role=RbacRoleEnum.OWNER,
                external_id=owner_user_id,
                email_verified=False,
            )
        )
        if not owner_auth:
            raise RuntimeError(f"Failed to create owner user: {owner_email}")

        _ = await self._create_user_in_tenant_db(
            database_url=database_url,
            email=owner_email,
            workos_user_id=owner_auth.id,
            role=RbacRoleEnum.OWNER,
            external_id=owner_auth.external_id,
        )
        logger.info(f"Created owner user: {owner_email}")

        emails = [
            self.admin_settings.support_user_email,
            "matias@flowrms.com",
            "derrick@flowrms.com",
            "mhr@flowrms.com",
            "junaid@flowrms.com",
            "kamal@flowrms.com",
            "holly@flowrms.com",
            "jamal@flowrms.com",
        ]
        emails = list(set(emails))
        for email in emails:
            support_user = await self.workos_service.create_user(
                AuthUserInput(
                    email=email,
                    first_name=email.split("@")[0].capitalize(),
                    last_name="Support",
                    tenant_id=workos_org.id,
                    role=RbacRoleEnum.ADMINISTRATOR,
                    email_verified=True,
                    external_id=uuid.uuid4(),
                )
            )
            if not support_user:
                logger.warning(f"Failed to create support user: {email}")
                continue

            _ = await self._create_user_in_tenant_db(
                database_url=database_url,
                email=email,
                workos_user_id=support_user.id,
                role=RbacRoleEnum.ADMINISTRATOR,
                external_id=support_user.external_id,
            )
        return TenantCreationResult(
            tenant=tenant,
            owner_workos_id=owner_auth.id,
            workos_org_id=workos_org.id,
            success=True,
            message=f"Tenant '{name}' created successfully",
        )

    async def list_tenants(self) -> list[Tenant]:
        return await self.repository.list_all()

    async def get_tenant(self, tenant_id: uuid.UUID) -> Tenant | None:
        return await self.repository.get_by_id(tenant_id)
