"""REST API routes for Gmail OAuth integration."""

import functools
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse

from app.core.config.base_settings import get_settings
from app.integrations.gmail.config import GmailSettings


@functools.cache
def get_gmail_settings() -> GmailSettings:
    """Get Gmail settings singleton."""
    return get_settings(GmailSettings)


router = APIRouter(prefix="/integrations/gmail", tags=["Gmail Integration"])


@router.get("/callback")
async def gmail_callback(
    request: Request,  # noqa: ARG001
    settings: Annotated[GmailSettings, Depends(get_gmail_settings)],
    code: str | None = Query(None),
    state: str | None = Query(None),
    error: str | None = Query(None),
) -> RedirectResponse:
    """
    OAuth callback endpoint for Gmail.

    This endpoint receives the authorization code from Google after user consent.
    It redirects to the frontend with the code or error information.

    The frontend should then call the gmailConnect GraphQL mutation with the code
    to complete the OAuth flow.

    Args:
        request: FastAPI request object
        settings: Gmail settings
        code: Authorization code from Google (on success)
        state: State parameter for CSRF protection
        error: Error code (on failure)

    Returns:
        Redirect to frontend with code or error in query params
    """
    # Get the frontend URL from redirect URI (strip the callback path)
    redirect_uri = settings.gmail_redirect_uri
    base_url = (
        redirect_uri.rsplit("/api/", 1)[0]
        if "/api/" in redirect_uri
        else redirect_uri.rsplit("/", 3)[0]
    )

    # Build redirect URL to frontend
    frontend_callback = f"{base_url}/settings/integrations/gmail"

    if error:
        # Redirect with error
        return RedirectResponse(url=f"{frontend_callback}?error={error}")

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
