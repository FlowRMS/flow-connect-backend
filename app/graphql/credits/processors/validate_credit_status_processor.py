from commons.db.v6.commission import Credit
from commons.db.v6.commission.credits.enums import CreditStatus

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent
from app.errors.common_errors import ValidationError


class ValidateCreditStatusProcessor(BaseProcessor[Credit]):
    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_UPDATE, RepositoryEvent.PRE_DELETE]

    async def process(self, context: EntityContext[Credit]) -> None:
        original = context.original_entity
        if original is None:
            return

        if original.status == CreditStatus.POSTED:
            raise ValidationError(
                f"Cannot modify credit '{original.credit_number}': credit is posted"
            )