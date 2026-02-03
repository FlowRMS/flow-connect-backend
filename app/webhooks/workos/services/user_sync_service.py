from typing import cast

from commons.db.controller import MultiTenantController
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from commons.db.v6.user import User
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from workos.types.user_management import OrganizationMembership
from workos.types.user_management import User as WorkOSUser
from workos.types.webhooks.webhook import UserCreatedWebhook

from app.admin.tenants.repositories.tenants_repository import TenantsRepository
from app.auth.workos_auth_service import WorkOSAuthService

WORKOS_ROLE_TO_RBAC: dict[str, RbacRoleEnum] = {
    "owner": RbacRoleEnum.OWNER,
    "administrator": RbacRoleEnum.ADMINISTRATOR,
    "admin": RbacRoleEnum.ADMINISTRATOR,
    "inside_rep": RbacRoleEnum.INSIDE_REP,
    "outside_rep": RbacRoleEnum.OUTSIDE_REP,
    "warehouse_manager": RbacRoleEnum.WAREHOUSE_MANAGER,
    "warehouse_employee": RbacRoleEnum.WAREHOUSE_EMPLOYEE,
    "driver": RbacRoleEnum.DRIVER,
}


class UserSyncService:
    def __init__(
        self,
        controller: MultiTenantController,
        tenants_repository: TenantsRepository,
        workos_service: WorkOSAuthService,
    ) -> None:
        super().__init__()
        self.controller = controller
        self.tenants_repository = tenants_repository
        self.workos_service = workos_service

    async def handle_user_created(self, event: UserCreatedWebhook) -> None:
        workos_user = event.data

        if workos_user.external_id:
            logger.debug(f"Skipping user {workos_user.email}: external_id already set")
            return

        membership = await self._get_first_organization_membership(workos_user.id)
        if not membership:
            logger.debug(
                f"Skipping user {workos_user.email}: no organization membership"
            )
            return

        org_id = membership.organization_id
        tenant = await self.tenants_repository.get_by_org_id(org_id)
        if not tenant:
            logger.warning(f"Tenant not found for org_id {org_id}")
            return

        async with self.controller.scoped_session(cast(str, tenant.url)) as session:
            async with session.begin():
                local_user = await self._find_user_by_email(session, workos_user.email)

                if local_user:
                    await self._sync_existing_user(
                        session=session,
                        local_user=local_user,
                        workos_user_id=workos_user.id,
                        membership=membership,
                    )
                else:
                    _ = await self._create_new_user(
                        session=session,
                        workos_user=workos_user,
                        membership=membership,
                    )

    async def _get_first_organization_membership(
        self, user_id: str
    ) -> OrganizationMembership | None:
        response = await self.workos_service.client.user_management.list_organization_memberships(
            user_id=user_id,
            limit=1,
        )
        if not response.data:
            return None
        return response.data[0]

    @staticmethod
    async def _find_user_by_email(session: AsyncSession, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def _sync_existing_user(
        self,
        session: AsyncSession,
        local_user: User,
        workos_user_id: str,
        membership: OrganizationMembership,
    ) -> None:
        if not local_user.auth_provider_id:
            local_user.auth_provider_id = workos_user_id
            _ = await session.flush([local_user])

        _ = await self.workos_service.client.user_management.update_user(
            user_id=workos_user_id,
            external_id=str(local_user.id),
        )

        workos_role_slug = membership.role.get("slug", "").lower()
        local_role_slug = local_user.role.name.lower()

        if workos_role_slug != local_role_slug:
            logger.info(
                f"Role mismatch for {local_user.email}: "
                f"WorkOS={workos_role_slug}, Local={local_role_slug}. "
                f"Updating WorkOS to match local."
            )
            _ = await self.workos_service.client.user_management.update_organization_membership(
                organization_membership_id=membership.id,
                role_slug=local_role_slug,
            )

    async def _create_new_user(
        self,
        session: AsyncSession,
        workos_user: WorkOSUser,
        membership: OrganizationMembership,
    ) -> User:
        workos_role_slug = membership.role.get("slug", "").lower()
        role = WORKOS_ROLE_TO_RBAC.get(workos_role_slug, RbacRoleEnum.INSIDE_REP)

        user = User(
            email=workos_user.email,
            username=workos_user.email,
            first_name=workos_user.first_name or "",
            last_name=workos_user.last_name or "",
            role=role,
            enabled=True,
        )
        user.auth_provider_id = workos_user.id

        session.add(user)
        _ = await session.flush([user])

        _ = await self.workos_service.client.user_management.update_user(
            user_id=workos_user.id,
            external_id=str(user.id),
        )

        logger.info(f"Created new user {user.email} with role {role.name}")
        return user
