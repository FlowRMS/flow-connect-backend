from typing import Annotated

from aioinject import Injected
from aioinject.ext.fastapi import inject
from fastapi import APIRouter, Header, HTTPException, Request
from loguru import logger
from workos.webhooks import Webhooks

from app.core.config.workos_settings import WorkOSSettings
from app.webhooks.workos.services.user_sync_service import UserSyncService

router = APIRouter()


@router.post("/")
@inject
async def handle_webhook(
    request: Request,
    user_sync_service: Injected[UserSyncService],
    workos_settings: Injected[WorkOSSettings],
    workos_signature: Annotated[str | None, Header(alias="WorkOS-Signature")] = None,
) -> dict[str, str]:
    if not workos_signature:
        raise HTTPException(status_code=401, detail="Missing WorkOS-Signature header")

    body = await request.body()

    webhooks = Webhooks()
    try:
        event = webhooks.verify_event(
            event_body=body,
            event_signature=workos_signature,
            secret=workos_settings.workos_webhook_secret,
        )
    except ValueError as e:
        logger.warning(f"Webhook signature verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid signature") from e

    if event.event == "user.created":
        await user_sync_service.handle_user_created(event)

    return {"status": "ok"}
