import functools
from typing import Annotated, Any

from commons.auth import KeycloakService
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.config.auth_settings import AuthSettings
from app.core.config.base_settings import get_settings


@functools.cache
def create_keycloak_service() -> KeycloakService:
    auth_settings = get_settings(AuthSettings)
    return KeycloakService(
        auth_settings.auth_url,
        auth_settings.client_id,
        auth_settings.client_secret,
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/refresh")
async def refresh_token(
    body: RefreshTokenRequest,
    keycloak: Annotated[KeycloakService, Depends(create_keycloak_service)],
) -> dict[str, Any]:
    """
    Refresh access token using refresh token.

    Args:
        body: Request body containing refresh_token
        keycloak: Injected KeycloakService

    Returns:
        Raw token response from Keycloak
    """
    response = await keycloak.generate_token(body.refresh_token)

    if response is None:
        raise HTTPException(status_code=401, detail="Failed to refresh token")

    return response
