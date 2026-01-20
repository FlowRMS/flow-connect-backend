
from commons.db.v6 import RecurringShipment

from app.core.processors import (
    BaseProcessor,
    EntityContext,
    RepositoryEvent,
)
from app.errors.common_errors import ValidationError
from app.graphql.v2.core.deliveries.utils.recurrence_utils import (
    validate_recurrence_pattern,
)


class ValidateRecurrencePatternProcessor(BaseProcessor[RecurringShipment]):
    """Validates recurrence pattern before create/update."""

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[RecurringShipment]) -> None:
        shipment = context.entity
        if not shipment.recurrence_pattern:
            return

        validation_error = validate_recurrence_pattern(shipment.recurrence_pattern)
        if validation_error:
            raise ValidationError(f"Invalid recurrence pattern: {validation_error}")
