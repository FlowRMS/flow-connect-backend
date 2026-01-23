from uuid import UUID

from commons.db.v6 import RecurringShipment
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper
from app.core.processors.executor import ProcessorExecutor
from app.graphql.base_repository import BaseRepository
from app.graphql.v2.core.deliveries.processors import (
    ValidateRecurrencePatternProcessor,
)


class RecurringShipmentsRepository(BaseRepository[RecurringShipment]):
    def __init__(
        self,
        context_wrapper: ContextWrapper,
        session: AsyncSession,
        processor_executor: ProcessorExecutor,
        validate_recurrence_processor: ValidateRecurrencePatternProcessor,
    ) -> None:
        super().__init__(
            session,
            context_wrapper,
            RecurringShipment,
            processor_executor=processor_executor,
            processor_executor_classes=[validate_recurrence_processor],
        )

    async def list_by_warehouse(self, warehouse_id: UUID) -> list[RecurringShipment]:
        stmt = select(RecurringShipment).where(
            RecurringShipment.warehouse_id == warehouse_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
