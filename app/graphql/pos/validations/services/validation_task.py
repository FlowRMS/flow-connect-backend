import asyncio
import logging
import uuid

logger = logging.getLogger(__name__)


def trigger_validation_task(file_id: uuid.UUID) -> None:
    asyncio.create_task(_run_validation_task(file_id))


async def _run_validation_task(file_id: uuid.UUID) -> None:
    try:
        from app.core.container import create_container

        container = create_container()
        async with container.context() as ctx:
            from app.graphql.pos.validations.services.validation_execution_service import (
                ValidationExecutionService,
            )

            service = await ctx.resolve(ValidationExecutionService)
            await service.validate_file(file_id)
    except Exception:
        logger.exception("Validation task failed for file %s", file_id)
