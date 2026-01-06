from uuid import UUID

from commons.auth import AuthInfo
from loguru import logger

from app.core.container import create_container
from app.core.context import Context, ContextModel
from app.core.context_wrapper import ContextWrapper
from app.workers.document_execution.executor_service import DocumentExecutorService


async def inner_execute_pending_document_task(
    pending_document_id: UUID,
    auth_info: AuthInfo,
) -> dict[str, object]:
    logger.info(
        f"Starting document execution for {pending_document_id} in {auth_info.tenant_name}"
    )

    container = create_container()

    async with container.context() as ctx:
        context = Context()
        context.initialize(ContextModel(auth_info=auth_info))
        context_wrapper = await ctx.resolve(ContextWrapper)
        token = context_wrapper.set(context)
        executor = await ctx.resolve(DocumentExecutorService)

        try:
            created_ids = await executor.execute(pending_document_id)
            logger.info(f"Created {len(created_ids)} entities")
            return {
                "status": "success",
                "count": len(created_ids),
            }

        except Exception as e:
            logger.exception(f"Error executing document {pending_document_id}: {e}")
            return {
                "status": "error",
                "error": str(e),
            }
        finally:
            context_wrapper.reset(token)
