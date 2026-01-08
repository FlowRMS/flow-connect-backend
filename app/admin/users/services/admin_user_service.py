import uuid

from commons.db.controller import MultiTenantController
from commons.db.models.tenant import Tenant
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from commons.db.v6.user import User
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.admin.tenants.repositories.tenants_repository import TenantsRepository
from app.admin.users.strawberry.user_inputs import (
    CreateAdminUserInput,
    UpdateAdminUserInput,
)
from app.admin.users.strawberry.user_types import AdminUserData
from app.auth.models import AuthUserInput
from app.auth.workos_auth_service import WorkOSAuthService
from app.core.config.settings import Settings


class AdminUserService:
    def __init__(
        self,
        tenants_repository: TenantsRepository,
        controller: MultiTenantController,
        workos_service: WorkOSAuthService,
        settings: Settings,
    ) -> None:
        super().__init__()
        self.tenants_repository = tenants_repository
        self.controller = controller
        self.workos_service = workos_service
        self.settings = settings

    async def _get_tenant_database_url(self, tenant: Tenant) -> str:
        return (
            self.settings.pg_url.unicode_string().rsplit("/", 1)[0] + f"/{tenant.url}"
        )

    async def _get_workos_org_id_for_tenant(self, tenant: Tenant) -> str | None:
        orgs = await self.workos_service.client.organizations.list_organizations()
        for org in orgs.data:
            if org.name == tenant.name:
                return org.id
        return None

    async def _query_users_from_tenant(
        self,
        tenant: Tenant,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AdminUserData]:
        results: list[AdminUserData] = []
        try:
            async with self.controller.scoped_session(tenant.url) as session:
                stmt = select(User).order_by(User.email).limit(limit).offset(offset)
                result = await session.execute(stmt)
                users = result.scalars().all()
                for user in users:
                    results.append(
                        AdminUserData.from_orm(
                            user,
                            tenant_id=tenant.id,
                            tenant_name=tenant.name,
                            tenant_url=tenant.url,
                        )
                    )
        except Exception as e:
            logger.warning(f"Failed to query users from tenant {tenant.url}: {e}")
        return results

    async def list_all_users(
        self,
        tenant_id: uuid.UUID | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AdminUserData]:
        if tenant_id:
            tenant = await self.tenants_repository.get_by_id(tenant_id)
            if not tenant:
                return []
            return await self._query_users_from_tenant(tenant, limit, offset)

        tenants = await self.tenants_repository.list_all()
        all_users: list[AdminUserData] = []
        for tenant in tenants:
            users = await self._query_users_from_tenant(tenant, limit, offset)
            all_users.extend(users)
        return all_users

    async def get_user(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> AdminUserData | None:
        tenant = await self.tenants_repository.get_by_id(tenant_id)
        if not tenant:
            return None

        try:
            async with self.controller.scoped_session(tenant.url) as session:
                stmt = select(User).where(User.id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                if not user:
                    return None
                return AdminUserData.from_orm(
                    user,
                    tenant_id=tenant.id,
                    tenant_name=tenant.name,
                    tenant_url=tenant.url,
                )
        except Exception as e:
            logger.error(f"Failed to get user {user_id} from tenant {tenant.url}: {e}")
            return None

    async def _check_user_exists_by_email(self, tenant: Tenant, email: str) -> bool:
        try:
            async with self.controller.scoped_session(tenant.url) as session:
                stmt = select(User).where(User.email == email)
                result = await session.execute(stmt)
                return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.warning(f"Failed to check user email in tenant {tenant.url}: {e}")
            return False

    async def create_user(self, input: CreateAdminUserInput) -> AdminUserData:
        tenant = await self.tenants_repository.get_by_id(input.tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {input.tenant_id} not found")

        if await self._check_user_exists_by_email(tenant, input.email):
            raise ValueError(f"User with email {input.email} already exists")

        workos_org_id = await self._get_workos_org_id_for_tenant(tenant)
        if not workos_org_id:
            raise ValueError(f"WorkOS organization not found for tenant {tenant.name}")

        username = input.username or input.email

        auth_user = await self.workos_service.create_user(
            AuthUserInput(
                email=input.email,
                tenant_id=workos_org_id,
                role=input.role,
                external_id=uuid.uuid4(),
                first_name=input.first_name,
                last_name=input.last_name,
                email_verified=False,
                metadata={
                    "enabled": str(input.enabled),
                },
            )
        )
        if not auth_user:
            raise RuntimeError(f"Failed to create user in WorkOS: {input.email}")

        database_url = await self._get_tenant_database_url(tenant)
        user = await self._create_user_in_tenant_db(
            database_url=database_url,
            user_id=auth_user.external_id,
            email=input.email,
            username=username,
            workos_user_id=auth_user.id,
            role=input.role,
            first_name=input.first_name,
            last_name=input.last_name,
            enabled=input.enabled,
            inside=input.inside,
            outside=input.outside,
            visible=input.visible,
        )

        return AdminUserData.from_orm(
            user,
            tenant_id=tenant.id,
            tenant_name=tenant.name,
            tenant_url=tenant.url,
        )

    async def _create_user_in_tenant_db(
        self,
        database_url: str,
        user_id: uuid.UUID,
        email: str,
        username: str,
        workos_user_id: str,
        role: RbacRoleEnum,
        first_name: str,
        last_name: str,
        enabled: bool = True,
        inside: bool | None = None,
        outside: bool | None = None,
        visible: bool | None = True,
    ) -> User:
        engine = create_async_engine(database_url)
        try:
            async with AsyncSession(engine) as session:
                async with session.begin():
                    user = User(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=email,
                        role=role,
                        enabled=enabled,
                        inside=inside,
                        outside=outside,
                        visible=visible,
                    )
                    user.id = user_id
                    user.auth_provider_id = workos_user_id
                    session.add(user)
                    logger.info(f"Created user {email} in tenant database")
                    return user
        finally:
            await engine.dispose()

    async def update_user(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        input: UpdateAdminUserInput,
    ) -> AdminUserData:
        tenant = await self.tenants_repository.get_by_id(tenant_id)
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")

        database_url = await self._get_tenant_database_url(tenant)
        engine = create_async_engine(database_url)
        try:
            async with AsyncSession(engine) as session:
                async with session.begin():
                    stmt = select(User).where(User.id == user_id)
                    result = await session.execute(stmt)
                    user = result.scalar_one_or_none()
                    if not user:
                        raise ValueError(f"User {user_id} not found")

                    if input.first_name is not None:
                        user.first_name = input.first_name
                    if input.last_name is not None:
                        user.last_name = input.last_name
                    if input.role is not None:
                        user.role = input.role
                    if input.enabled is not None:
                        user.enabled = input.enabled
                    if input.inside is not None:
                        user.inside = input.inside
                    if input.outside is not None:
                        user.outside = input.outside
                    if input.email is not None:
                        user.email = input.email
                    if input.username is not None:
                        user.username = input.username

                    if input.visible is not None:
                        user.visible = input.visible

                    await session.flush([user])

                    if input.first_name is not None or input.last_name is not None:
                        _ = await self.workos_service.update_user(
                            user_id=user.auth_provider_id,
                            auth_user_input=AuthUserInput(
                                email=user.email,
                                tenant_id="",
                                role=user.role,
                                external_id=user.id,
                                first_name=user.first_name,
                                last_name=user.last_name,
                                metadata={
                                    "enabled": str(user.enabled),
                                },
                            ),
                        )

                    return AdminUserData.from_orm(
                        user,
                        tenant_id=tenant.id,
                        tenant_name=tenant.name,
                        tenant_url=tenant.url,
                    )
        finally:
            await engine.dispose()
