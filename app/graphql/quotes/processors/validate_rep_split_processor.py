from decimal import Decimal

from commons.db.v6.crm.quotes import Quote

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent
from app.errors.common_errors import ValidationError


class ValidateRepSplitProcessor(BaseProcessor[Quote]):
    """
    Validates that rep split percentages on each quote line are valid.

    Rules:
    - Each split_rate must be between 0 and 100 (inclusive)
    - Total split rates per line cannot exceed 100%
    """

    def __init__(self) -> None:
        super().__init__()

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Quote]) -> None:
        quote = context.entity

        for detail in quote.details:
            if not detail.split_rates:
                continue

            total_split = Decimal("0")

            for split in detail.split_rates:
                if split.split_rate < Decimal("0"):
                    raise ValidationError(
                        f"Split rate cannot be negative on line {detail.item_number}. "
                        f"Got: {split.split_rate}%"
                    )

                if split.split_rate > Decimal("100"):
                    raise ValidationError(
                        f"Split rate cannot exceed 100% on line {detail.item_number}. "
                        f"Got: {split.split_rate}%"
                    )

                total_split += split.split_rate

            if total_split > Decimal("100"):
                raise ValidationError(
                    f"Total split rates on line {detail.item_number} exceed 100%. "
                    f"Total: {total_split}%"
                )
