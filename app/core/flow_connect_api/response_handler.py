import json

import httpx

from app.errors.common_errors import (
    ConflictError,
    NotFoundError,
    RemoteApiError,
    UnauthorizedError,
)


def raise_for_api_status(
    response: httpx.Response,
    *,
    entity_id: str | None = None,
    context: str | None = None,
) -> None:
    status = response.status_code

    if 200 <= status < 300:
        return

    if status == 400:
        message = _extract_remote_message(response)
        raise RemoteApiError(
            _with_context(f"Remote API: {message}", context), status_code=status
        )

    if status in (401, 403):
        raise UnauthorizedError("Not authorized to perform this action")

    if status == 404:
        raise NotFoundError(entity_id or "unknown")

    if status == 409:
        raise ConflictError("Resource conflict")

    if status >= 500:
        message = _extract_remote_message(
            response, fallback=f"Remote API error: {status}"
        )
        raise RemoteApiError(_with_context(message, context), status_code=status)

    raise RemoteApiError(f"Unexpected response: {status}", status_code=status)


def _extract_remote_message(
    response: httpx.Response,
    fallback: str = "Bad request",
) -> str:
    try:
        data = response.json()
        return data.get("message", fallback)
    except (json.JSONDecodeError, AttributeError, ValueError):
        return fallback


def _with_context(message: str, context: str | None) -> str:
    if context:
        return f"{context}: {message}"
    return message
