"""REST API routes for Microsoft O365 OAuth integration."""

import functools
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.core.config.base_settings import get_settings
from app.integrations.microsoft_o365.config import O365Settings


@functools.cache
def get_o365_settings() -> O365Settings:
    """Get O365 settings singleton."""
    return get_settings(O365Settings)


router = APIRouter(prefix="/integrations/o365", tags=["O365 Integration"])


@router.get("/callback")
async def o365_callback(
    request: Request,  # noqa: ARG001
    settings: Annotated[O365Settings, Depends(get_o365_settings)],
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    error_description: str | None = None,
) -> RedirectResponse:
    """
    OAuth callback endpoint for Microsoft O365.

    This endpoint receives the authorization code from Microsoft after user consent.
    It redirects to the frontend with the code or error information.

    The frontend should then call the o365_connect GraphQL mutation with the code
    to complete the OAuth flow.

    Args:
        request: FastAPI request object
        settings: O365 settings
        code: Authorization code from Microsoft (on success)
        state: State parameter for CSRF protection
        error: Error code (on failure)
        error_description: Human-readable error description (on failure)

    Returns:
        Redirect to frontend with code or error in query params
    """
    # Get the frontend URL from redirect URI (strip the callback path)
    # e.g., "https://app.example.com/api/integrations/o365/callback" -> "https://app.example.com"
    redirect_uri = settings.o365_redirect_uri
    base_url = (
        redirect_uri.rsplit("/api/", 1)[0]
        if "/4/" in redirect_uri
        else redirect_uri.rsplit("/", 3)[0]
    )

    # Build redirect URL to frontend
    frontend_callback = f"{base_url}/settings/integrations/o365"

    if error:
        # Redirect with error
        return RedirectResponse(
            url=f"{frontend_callback}?error={error}&error_description={error_description or ''}"
        )

    if code:
        # Redirect with code and state
        redirect_url = f"{frontend_callback}?code={code}"
        if state:
            redirect_url += f"&state={state}"
        return RedirectResponse(url=redirect_url)

    # No code or error - something went wrong
    return RedirectResponse(
        url=f"{frontend_callback}?error=unknown&error_description=No code or error received"
    )
