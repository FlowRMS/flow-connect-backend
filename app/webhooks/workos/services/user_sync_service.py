import uuid
from typing import cast

from commons.db.controller import MultiTenantController
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from commons.db.v6.user import User
from loguru import logger
from workos.types.user_management import OrganizationMembership
from workos.types.user_management import User as WorkOSUser
from workos.types.webhooks.webhook import UserCreatedWebhook

from app.admin.tenants.repositories.tenants_repository import TenantsRepository
from app.auth.workos_auth_service import WorkOSAuthService
from app.webhooks.workos.repositories.webhook_user_repository import (
    WebhookUserRepository,
)

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

        user_id, role_slug_for_sync = await self._persist_user(
            tenant_url=cast(str, tenant.url),
            workos_user=workos_user,
            membership=membership,
        )

        await self._sync_to_workos(
            workos_user_id=workos_user.id,
            local_user_id=user_id,
            membership=membership,
            role_slug_for_sync=role_slug_for_sync,
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

    async def _persist_user(
        self,
        tenant_url: str,
        workos_user: WorkOSUser,
        membership: OrganizationMembership,
    ) -> tuple[uuid.UUID, str | None]:
        async with self.controller.scoped_session(tenant_url) as session:
            async with session.begin():
                repo = WebhookUserRepository(session)
                local_user = await repo.get_by_email(workos_user.email)

                if local_user:
                    if not local_user.auth_provider_id:
                        local_user.auth_provider_id = workos_user.id
                        await repo.update(local_user)
                    return local_user.id, self._get_role_mismatch(
                        local_user, membership
                    )

                new_user = self._build_new_user(workos_user, membership)
                new_user = await repo.create(new_user)
                logger.info(
                    f"Created new user {new_user.email} with role {new_user.role.name}"
                )
                return new_user.id, None

    async def _sync_to_workos(
        self,
        workos_user_id: str,
        local_user_id: uuid.UUID,
        membership: OrganizationMembership,
        role_slug_for_sync: str | None,
    ) -> None:
        _ = await self.workos_service.client.user_management.update_user(
            user_id=workos_user_id,
            external_id=str(local_user_id),
        )

        if role_slug_for_sync:
            logger.info(
                f"Role mismatch: updating WorkOS to match local "
                f"role={role_slug_for_sync}"
            )
            _ = await self.workos_service.client.user_management.update_organization_membership(
                organization_membership_id=membership.id,
                role_slug=role_slug_for_sync,
            )

    @staticmethod
    def _get_role_mismatch(
        local_user: User,
        membership: OrganizationMembership,
    ) -> str | None:
        workos_role_slug = membership.role.get("slug", "").lower()
        local_role_slug = local_user.role.name.lower()
        if workos_role_slug != local_role_slug:
            return local_role_slug
        return None

    @staticmethod
    def _build_new_user(
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
        return user
