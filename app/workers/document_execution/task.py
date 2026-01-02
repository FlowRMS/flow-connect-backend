from uuid import UUID

from commons.db.controller import MultiTenantController
from commons.db.v6.ai.documents.pending_document import PendingDocument
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config.settings import Settings
from app.core.container import create_container
from app.workers.broker import broker

from .executor_service import DocumentExecutorService


async def get_multitenant_controller(settings: Settings) -> MultiTenantController:
    controller = MultiTenantController(
        pg_url=settings.pg_url.unicode_string(),
        app_name="Document Executor Worker",
        echo=settings.log_level == "DEBUG",
        connect_args={"timeout": 5, "command_timeout": 90},
        env=settings.environment,
    )
    await controller.load_data_sources()
    return controller


@broker.task
async def execute_pending_document_task(
    pending_document_id: UUID,
    tenant_name: str,
) -> dict[str, object]:
    logger.info(
        f"Starting document execution for {pending_document_id} in {tenant_name}"
    )

    container = create_container()

    async with container.context() as ctx:
        settings = await ctx.resolve(Settings)
        controller = await get_multitenant_controller(settings)

        try:
            async with controller.scoped_session(tenant_name) as session:
                async with session.begin():
                    stmt = (
                        select(PendingDocument)
                        .where(PendingDocument.id == pending_document_id)
                        .options(selectinload(PendingDocument.pending_entities))
                    )
                    result = await session.execute(stmt)
                    pending_doc = result.scalar_one_or_none()

                    if not pending_doc:
                        logger.error(f"PendingDocument {pending_document_id} not found")
                        return {
                            "status": "error",
                            "error": "Document not found",
                        }

                    executor = DocumentExecutorService(session=session)
                    created_ids = await executor.execute(pending_doc)

                    logger.info(f"Created {len(created_ids)} entities")

                    return {
                        "status": "success",
                        "created_entity_ids": [str(id) for id in created_ids],
                        "count": len(created_ids),
                    }

        except Exception as e:
            logger.exception(f"Error executing document {pending_document_id}: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
