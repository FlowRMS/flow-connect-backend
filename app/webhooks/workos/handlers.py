from loguru import logger

from app.tenant_provisioning.service import (
    ProvisioningStatus,
    TenantProvisioningService,
)
from app.webhooks.workos.schemas import WorkOSEvent


async def handle_organization_created(
    event: WorkOSEvent,
    provisioning_service: TenantProvisioningService,
) -> None:
    """
    Handle organization.created webhook event.

    This handler is called when a new organization is created in WorkOS.
    It triggers the tenant provisioning flow.
    """
    logger.info(
        "Received organization.created event",
        event_id=event.id,
        org_id=event.data.id,
        org_name=event.data.name,
    )

    result = await provisioning_service.provision(
        org_id=event.data.id,
        org_name=event.data.name,
    )

    if result.status == ProvisioningStatus.CREATED:
        logger.info(
            "Tenant provisioned successfully",
            tenant_id=result.tenant_id,
            org_id=event.data.id,
        )
    elif result.status == ProvisioningStatus.ALREADY_EXISTS:
        logger.info(
            "Tenant already exists",
            tenant_id=result.tenant_id,
            org_id=event.data.id,
        )
    else:
        logger.error(
            "Tenant provisioning failed",
            org_id=event.data.id,
            error=result.error,
        )
