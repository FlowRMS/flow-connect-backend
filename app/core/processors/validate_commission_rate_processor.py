from typing import TypeVar

from commons.db.v6.models import Invoice, Order, Quote

from app.core.processors import (
    BaseProcessor,
    EntityContext,
    RepositoryEvent,
    validate_commission_rate_max,
)

Model = TypeVar("Model", Quote, Order, Invoice)


class ValidateCommissionRateProcessor(BaseProcessor[Model]):
    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Model]) -> None:
        entity = context.entity
        validate_commission_rate_max(entity.details)
