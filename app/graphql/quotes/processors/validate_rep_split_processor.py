from commons.db.v6.crm.quotes import Quote

from app.core.processors import (
    BaseProcessor,
    EntityContext,
    RepositoryEvent,
    validate_split_rate_range,
    validate_split_rates_sum_to_100,
)


class ValidateRepSplitProcessor(BaseProcessor[Quote]):
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

            context_msg = f"on line {detail.item_number}"
            validate_split_rate_range(
                detail.split_rates,
                label="split rate",
                context=context_msg,
            )
            validate_split_rates_sum_to_100(
                detail.split_rates,
                label=f"split rates {context_msg}",
            )
