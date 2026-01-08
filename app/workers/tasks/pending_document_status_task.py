import asyncio
from dataclasses import dataclass
from uuid import UUID

from commons.db.controller import MultiTenantController
from commons.db.v6.ai.documents.pending_document import PendingDocument
from commons.db.v6.ai.documents.pending_document_processing import (
    PendingDocumentProcessing,
)
from commons.db.v6.enums import WorkflowStatus
from commons.db.v6.user import User
from loguru import logger
from sqlalchemy import select

from app.core.config.resend_settings import ResendSettings
from app.core.config.settings import Settings
from app.core.container import create_container
from app.workers.services.resend_notification_service import ResendNotificationService
from app.workers.tasks.pending_document_email_builder import (
    build_pending_document_status_email,
)

POLL_INTERVAL_SECONDS = 5
MAX_POLL_ATTEMPTS = 120  # 10 minutes max


@dataclass
class PendingDocumentStatusItem:
    pending_document_id: str
    tenant: str
    user_id: str


async def get_multitenant_controller(settings: Settings) -> MultiTenantController:
    controller = MultiTenantController(
        pg_url=settings.pg_url.unicode_string(),
        app_name="Pending Document Status Worker",
        echo=settings.log_level == "DEBUG",
        connect_args={
            "timeout": 5,
            "command_timeout": 90,
        },
        env=settings.environment,
    )
    await controller.load_data_sources()
    return controller


async def poll_pending_document_status(item: PendingDocumentStatusItem) -> None:
    logger.info(
        f"Starting status polling for pending document {item.pending_document_id}"
    )

    container = create_container()

    async with container.context() as ctx:
        settings = await ctx.resolve(Settings)
        resend_settings = await ctx.resolve(ResendSettings)
        controller = await get_multitenant_controller(settings)
        notification_service = ResendNotificationService(resend_settings)

        pending_document_id = UUID(item.pending_document_id)
        user_id = UUID(item.user_id)

        for attempt in range(MAX_POLL_ATTEMPTS):
            try:
                async with controller.scoped_session(item.tenant) as session:
                    async with session.begin():
                        pending_doc = await session.get(
                            PendingDocument, pending_document_id
                        )

                        if not pending_doc:
                            logger.error(
                                f"Pending document {pending_document_id} not found"
                            )
                            return

                        status = pending_doc.workflow_status
                        logger.info(f"Poll attempt {attempt + 1}: status = {status}")

                        if status != WorkflowStatus.IN_PROGRESS:
                            processing_stmt = select(PendingDocumentProcessing).where(
                                PendingDocumentProcessing.pending_document_id
                                == pending_document_id
                            )
                            processing_result = await session.execute(processing_stmt)
                            processing_records = list(processing_result.scalars().all())

                            user = await session.get(User, user_id)
                            if not user or not user.email:
                                logger.warning(
                                    f"User {user_id} not found or has no email"
                                )
                                return

                            # frontend_base_url = f"https://{item.tenant}.app.flowrms.com"
                            if settings.environment == "production":
                                frontend_base_url = "https://console.flowrms.com"
                            else:
                                frontend_base_url = f"https://{settings.environment}.console.flowrms.com"

                            html_body = build_pending_document_status_email(
                                pending_document=pending_doc,
                                processing_records=processing_records,
                                user=user,
                                tenant=item.tenant,
                                frontend_base_url=frontend_base_url,
                            )

                            subject = _build_email_subject(pending_doc)
                            result = notification_service.send_email(
                                to=user.email,
                                subject=subject,
                                html_body=html_body,
                            )

                            if result.success:
                                logger.info(
                                    f"Status email sent for document "
                                    f"{pending_document_id}: {result.message_id}"
                                )
                            else:
                                logger.error(
                                    f"Failed to send status email: {result.error}"
                                )
                            return

            except Exception as e:
                logger.exception(f"Error polling document status: {e}")

            await asyncio.sleep(POLL_INTERVAL_SECONDS)

        logger.warning(f"Max poll attempts reached for document {pending_document_id}")


def _build_email_subject(pending_doc: PendingDocument) -> str:
    status = pending_doc.workflow_status
    entity_type = (
        pending_doc.entity_type.name.replace("_", " ").title()
        if pending_doc.entity_type
        else "Document"
    )

    if status == WorkflowStatus.COMPLETED:
        return f"FlowAI: {entity_type} Processing Completed"
    elif status == WorkflowStatus.FAILED:
        return f"FlowAI: {entity_type} Processing Failed"
    elif status == WorkflowStatus.PAUSED:
        return f"FlowAI: {entity_type} Processing Paused"
    return f"FlowAI: {entity_type} Processing Status Update"
