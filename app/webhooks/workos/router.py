from fastapi import APIRouter, Header, HTTPException, Request
from loguru import logger

from app.tenant_provisioning.service import TenantProvisioningService
from app.webhooks.workos.handlers import handle_organization_created
from app.webhooks.workos.schemas import WorkOSEvent
from app.webhooks.workos.signature import (
    InvalidSignatureError,
    MissingSignatureError,
    SignatureExpiredError,
    verify_signature,
)

SUPPORTED_EVENTS = {"organization.created"}


def create_workos_webhook_router(
    webhook_secret: str,
    *,
    provisioning_service: TenantProvisioningService,
) -> APIRouter:
    """
    Create a FastAPI router for WorkOS webhooks.

    Args:
        webhook_secret: The webhook secret from WorkOS dashboard
        provisioning_service: Service for provisioning new tenants
    """
    router = APIRouter(tags=["webhooks"])

    @router.post("/webhooks/workos")
    async def handle_workos_webhook(
        request: Request,
        workos_signature: str | None = Header(None, alias="WorkOS-Signature"),
    ) -> dict[str, str]:
        """
        Handle incoming WorkOS webhook events.

        Verifies the signature and routes to appropriate handlers.
        """
        # Get raw body for signature verification
        body = await request.body()

        # Verify signature
        if not workos_signature:
            logger.warning("Webhook request missing signature header")
            raise HTTPException(status_code=401, detail="Missing signature")

        try:
            verify_signature(body, workos_signature, webhook_secret)
        except (
            MissingSignatureError,
            InvalidSignatureError,
            SignatureExpiredError,
        ) as e:
            logger.warning("Webhook signature verification failed", error=str(e))
            raise HTTPException(status_code=401, detail="Invalid signature") from e

        # Parse event
        event = WorkOSEvent.model_validate_json(body)
        logger.info(
            "Received WorkOS webhook", event_type=event.event, event_id=event.id
        )

        # Route to handler
        if event.event not in SUPPORTED_EVENTS:
            logger.debug("Ignoring unsupported event type", event_type=event.event)
            return {"status": "ok", "message": "Event ignored"}

        if event.event == "organization.created":
            await handle_organization_created(event, provisioning_service)

        return {"status": "ok"}

    return router
