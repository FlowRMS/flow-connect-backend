import uuid
from typing import Any

from commons.db.v6.rbac.rbac_role_enum import RbacRoleEnum
from pydantic import BaseModel


class AuthUserInput(BaseModel):
    email: str
    tenant_id: str
    role: RbacRoleEnum
    external_id: uuid.UUID
    first_name: str | None = None
    last_name: str | None = None
    email_verified: bool = False
    metadata: dict[str, Any] | None = None


class AuthUser(BaseModel):
    id: str
    email: str
    external_id: uuid.UUID
    tenant_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email_verified: bool = False
    metadata: dict[str, Any] | None = None


class AuthTenant(BaseModel):
    id: str
    name: str
    metadata: dict[str, Any] | None = None


class AuthMembership(BaseModel):
    id: str
    user_id: str
    organization_id: str
    role: str | None = None
    metadata: dict[str, Any] | None = None


class AuthenticationResult(BaseModel):
    user: AuthUser
    access_token: str
    refresh_token: str | None = None
    organization_id: str | None = None
    expires_in: int | None = None


class TokenPayload(BaseModel):
    sub: str
    external_id: uuid.UUID
    exp: int
    iat: int
    sid: str | None = None
    roles: list[str]
    tenant_id: str | None = None
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    metadata: dict[str, Any] | None = None
