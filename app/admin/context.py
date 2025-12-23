from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from fastapi import Request
from strawberry.fastapi import BaseContext

from app.admin.config.admin_settings import AdminSettings
from app.auth.models import TokenPayload
from app.auth.workos_auth_service import WorkOSAuthService


@dataclass
class AdminContextModel:
    admin_user_id: str
    email: str
    roles: list[str]
    external_id: str


class AdminContext(BaseContext):
    def __init__(self) -> None:
        super().__init__()
        self.admin_info: AdminContextModel | None = None
        self.aioinject_context: Any = None

    def initialize(self, context_model: AdminContextModel) -> None:
        self.admin_info = context_model

    @classmethod
    @asynccontextmanager
    async def set_context(
        cls,
        request: Request,
        workos_service: WorkOSAuthService,
        admin_settings: AdminSettings,
    ) -> AsyncGenerator[AdminContextModel, None]:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise PermissionError("Missing or invalid Authorization header")

        access_token = auth_header.replace("Bearer ", "")
        token_payload: TokenPayload = await workos_service.verify_access_token(
            access_token
        )

        if token_payload.tenant_id != admin_settings.admin_org_id:
            raise PermissionError(
                "Access denied. User is not a member of the admin organization."
            )

        yield AdminContextModel(
            admin_user_id=token_payload.sub,
            email=token_payload.email or "",
            roles=token_payload.roles,
            external_id=str(token_payload.external_id),
        )


async def get_admin_context() -> AdminContext:
    return AdminContext()
