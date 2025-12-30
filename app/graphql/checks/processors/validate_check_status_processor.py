from commons.db.v6.commission import Check
from commons.db.v6.commission.checks.enums import CheckStatus

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent
from app.errors.common_errors import ValidationError


class ValidateCheckStatusProcessor(BaseProcessor[Check]):
    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_UPDATE, RepositoryEvent.PRE_DELETE]

    async def process(self, context: EntityContext[Check]) -> None:
        original = context.original_entity
        if original is None:
            return

        if original.status == CheckStatus.POSTED:
            raise ValidationError(
                f"Cannot modify check '{original.check_number}': check is posted"
            )
