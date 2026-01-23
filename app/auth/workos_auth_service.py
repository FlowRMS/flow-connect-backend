import uuid
from typing import Any

import jwt
from jwt import PyJWKClient
from loguru import logger
from workos import AsyncWorkOSClient
from workos.exceptions import AuthorizationException
from workos.types.user_management.user import User as WorkOSUser

from app.auth.models import (
    AuthenticationResult,
    AuthTenant,
    AuthUser,
    AuthUserInput,
    TokenPayload,
)
from app.core.config.workos_settings import WorkOSSettings


class WorkOSAuthService:
    def __init__(self, workos_settings: WorkOSSettings) -> None:
        super().__init__()
        self.client = AsyncWorkOSClient(
            api_key=workos_settings.workos_api_key,
            client_id=workos_settings.workos_client_id,
        )
        self.client_id = workos_settings.workos_client_id
        self._jwks_client = PyJWKClient(
            uri=f"https://api.workos.com/sso/jwks/{workos_settings.workos_client_id}",
            cache_keys=True,
        )

    def _build_auth_user(
        self, user: WorkOSUser, tenant_id: str | None = None
    ) -> AuthUser:
        return AuthUser(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            external_id=uuid.UUID(user.external_id)
            if user.external_id
            else uuid.uuid4(),
            email_verified=user.email_verified,
            tenant_id=tenant_id,
            metadata=user.metadata,
        )

    def _build_authentication_result(self, response: Any) -> AuthenticationResult:
        return AuthenticationResult(
            user=self._build_auth_user(
                response.user,
                tenant_id=getattr(response, "organization_id", None),
            ),
            access_token=response.access_token,
            refresh_token=getattr(response, "refresh_token", None),
            organization_id=getattr(response, "organization_id", None),
            expires_in=getattr(response, "expires_in", None),
        )

    async def authenticate_with_pending_token(
        self, pending_authentication_token: str, organization_id: str
    ) -> AuthenticationResult | None:
        try:
            response = await self.client.user_management.authenticate_with_organization_selection(
                pending_authentication_token=pending_authentication_token,
                organization_id=organization_id,
            )
            return self._build_authentication_result(response)
        except AuthorizationException as e:
            logger.warning(f"Authorization failed: {e.response_json}")
            return None
        except Exception as e:
            logger.exception(f"Error authenticating with pending token: {e}")
            return None

    async def authenticate(
        self, email: str, password: str, tenant_id: str | None = None
    ) -> AuthenticationResult | None:
        try:
            response = await self.client.user_management.authenticate_with_password(
                email=email,
                password=password,
            )
            if not response:
                return None
            return self._build_authentication_result(response)
        except AuthorizationException as e:
            logger.warning(f"Authorization failed for {email}: {e.response_json}")
            pending_token = (
                e.response_json.get("pending_authentication_token", "")
                if e.response_json
                else ""
            )
            if not pending_token or not tenant_id:
                return None
            return await self.authenticate_with_pending_token(
                pending_authentication_token=pending_token,
                organization_id=tenant_id,
            )
        except Exception as e:
            logger.exception(f"Error authenticating with password: {e}")
            return None

    async def verify_access_token(self, access_token: str) -> TokenPayload:
        if not access_token or access_token.strip() == "":
            raise ValueError("Access token is missing")

        signing_key = self._jwks_client.get_signing_key_from_jwt(access_token)
        decoded = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_signature": True, "verify_exp": True},
        )
        return TokenPayload(
            sub=decoded["sub"],
            exp=decoded["exp"],
            iat=decoded["iat"],
            sid=decoded.get("sid"),
            roles=decoded.get("roles", []),
            tenant_id=decoded.get("org_id") or decoded.get("tid"),
            email=decoded.get("email"),
            first_name=decoded.get("firstName") or decoded.get("first_name"),
            last_name=decoded.get("lastName") or decoded.get("last_name"),
            external_id=uuid.UUID(decoded["external_id"]),
        )

    async def link_user_to_tenant(
        self, user_id: str, tenant_id: str, role: str
    ) -> str | None:
        try:
            membership = (
                await self.client.user_management.create_organization_membership(
                    user_id=user_id,
                    organization_id=tenant_id,
                    role_slug=role.lower(),
                )
            )
            return membership.organization_id
        except Exception as e:
            logger.exception(f"Error linking user to tenant: {e}")
            return None

    async def create_user(self, auth_user_input: AuthUserInput) -> AuthUser | None:
        try:
            existing_users = await self.client.user_management.list_users(
                email=auth_user_input.email,
            )
            if len(existing_users.data) > 0:
                workos_user = existing_users.data[0]
            else:
                workos_user = await self.client.user_management.create_user(
                    email=auth_user_input.email,
                    first_name=auth_user_input.first_name,
                    last_name=auth_user_input.last_name,
                    email_verified=auth_user_input.email_verified,
                    external_id=str(auth_user_input.external_id),
                    metadata=auth_user_input.metadata,
                )

            org_id = await self.link_user_to_tenant(
                user_id=workos_user.id,
                tenant_id=auth_user_input.tenant_id,
                role=auth_user_input.role.name.lower(),
            )
            if not org_id:
                logger.error(
                    f"Failed to link user {workos_user.email} to tenant {auth_user_input.tenant_id}"
                )
                return None

            return self._build_auth_user(workos_user, tenant_id=org_id)
        except Exception as e:
            logger.exception(f"Error creating user: {e}")
            return None

    async def get_user(self, user_id: str) -> AuthUser | None:
        try:
            response = await self.client.user_management.get_user(user_id=user_id)
            return self._build_auth_user(response)
        except Exception as e:
            logger.exception(f"Error getting user: {e}")
            return None

    async def list_users(self, email: str) -> list[AuthUser]:
        try:
            users = await self.client.user_management.list_users(email=email, limit=10)
            return [self._build_auth_user(user) for user in users.data]
        except Exception as e:
            logger.exception(f"Error listing users: {e}")
            return []

    async def update_user(
        self, user_id: str, auth_user_input: AuthUserInput
    ) -> AuthUser | None:
        try:
            response = await self.client.user_management.update_user(
                user_id=user_id,
                first_name=auth_user_input.first_name,
                last_name=auth_user_input.last_name,
                metadata=auth_user_input.metadata,
            )
            return self._build_auth_user(response)
        except Exception as e:
            logger.exception(f"Error updating user: {e}")
            return None

    async def delete_user(self, user_id: str) -> bool:
        try:
            await self.client.user_management.delete_user(user_id)
            return True
        except Exception as e:
            logger.exception(f"Error deleting user: {e}")
            return False

    async def remove_user_from_tenant(self, membership_id: str) -> bool:
        try:
            await self.client.user_management.delete_organization_membership(
                organization_membership_id=membership_id
            )
            return True
        except Exception as e:
            logger.exception(f"Error removing user from tenant: {e}")
            return False

    async def create_tenant(self, name: str, external_id: str) -> AuthTenant | None:
        try:
            response = await self.client.organizations.create_organization(
                name=name, external_id=external_id
            )
            return AuthTenant(id=response.id, name=response.name)
        except Exception as e:
            logger.exception(f"Error creating tenant: {e}")
            return None

    async def get_tenant(self, tenant_id: str) -> AuthTenant | None:
        try:
            response = await self.client.organizations.get_organization(
                organization_id=tenant_id
            )
            return AuthTenant(id=response.id, name=response.name)
        except Exception as e:
            logger.exception(f"Error getting tenant: {e}")
            return None

    async def delete_tenant(self, tenant_id: str) -> bool:
        try:
            await self.client.organizations.delete_organization(tenant_id)
            return True
        except Exception as e:
            logger.exception(f"Error deleting tenant: {e}")
            return False

    async def list_tenants_for_user(self, email: str) -> list[str]:
        try:
            users = await self.client.user_management.list_users(email=email, limit=1)
            if len(users.data) == 0:
                return []
            user = users.data[0]
            orgs = await self.client.user_management.list_organization_memberships(
                user_id=user.id, limit=10
            )
            return [org.organization_id for org in orgs.data]
        except Exception as e:
            logger.exception(f"Error listing tenants for user: {e}")
            return []
