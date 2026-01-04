from uuid import UUID

from commons.db.controller import MultiTenantController
from loguru import logger

from app.core.container import create_container
from app.workers.broker import broker

from .executor_service import DocumentExecutorService


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
        controller = await ctx.resolve(MultiTenantController)
        executor = await ctx.resolve(DocumentExecutorService)

        try:
            async with controller.scoped_session(tenant_name) as session:
                async with session.begin():
                    created_ids = await executor.execute(pending_document_id)
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
