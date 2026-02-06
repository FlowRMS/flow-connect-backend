import uuid
from typing import Any, override

import jwt
import pendulum
from commons.auth.auth_info import AuthInfo
from commons.auth.provider_enum import AuthProviderEnum
from commons.auth.strategies.workos import WorkOSService
from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from result import Err, Ok, Result

ROLE_MAPPING: dict[str, RbacRoleEnum] = {
    "MEMBER": RbacRoleEnum.INSIDE_REP,
}

DEFAULT_ROLE = RbacRoleEnum.INSIDE_REP


class FlowConnectWorkOSService(WorkOSService):
    def __init__(
        self,
        api_key: str,
        client_id: str,
        role_mapping: dict[str, RbacRoleEnum] | None = None,
        default_role: RbacRoleEnum = DEFAULT_ROLE,
    ) -> None:
        super().__init__(api_key=api_key, client_id=client_id)
        self._role_mapping: dict[str, RbacRoleEnum] = role_mapping or ROLE_MAPPING
        self._default_role: RbacRoleEnum = default_role

    def _map_role(self, role: str) -> RbacRoleEnum:
        return self._role_mapping.get(role.upper(), self._default_role)

    @override
    async def generate_auth_info_from_token(
        self, access_token: str
    ) -> Result[AuthInfo, Exception]:
        try:
            signing_key = self._jwks_client.get_signing_key_from_jwt(access_token)

            decoded: dict[str, Any] = jwt.decode(
                access_token,
                signing_key.key,
                algorithms=["RS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                },
            )

            roles: list[str] = decoded.get("roles", [])

            external_id = decoded.get("external_id")
            if external_id:
                flow_user_id = uuid.UUID(str(external_id))
            else:
                sub = decoded.get("sub", "")
                flow_user_id = uuid.uuid5(uuid.NAMESPACE_URL, sub)

            auth_info = AuthInfo(
                access_token=access_token,
                session_id=str(decoded.get("sid", "")),
                tenant_name=str(decoded.get("org_name", "")),
                tenant_id=str(decoded.get("org_id", "")),
                auth_provider_id=str(decoded.get("sub", "")),
                flow_user_id=flow_user_id,
                roles=[self._map_role(role) for role in roles],
                expires_at=pendulum.from_timestamp(int(decoded["exp"]), "UTC"),
                provider_type=AuthProviderEnum.WORKOS,
            )

            return Ok(auth_info)

        except jwt.ExpiredSignatureError as e:
            return Err(e)
        except jwt.InvalidTokenError as e:
            return Err(e)
        except Exception as e:
            return Err(e)
