from commons.db.v6.commission import Credit

from app.core.processors import (
    BaseProcessor,
    EntityContext,
    RepositoryEvent,
    validate_split_rate_range,
    validate_split_rates_sum_to_100,
)


class ValidateCreditSplitRateProcessor(BaseProcessor[Credit]):
    def __init__(self) -> None:
        super().__init__()

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Credit]) -> None:
        credit = context.entity

        for detail in credit.details:
            if not detail.outside_split_rates:
                continue

            context_msg = f"on line {detail.item_number}"
            validate_split_rate_range(
                detail.outside_split_rates,
                label="split rate",
                context=context_msg,
            )
            validate_split_rates_sum_to_100(
                detail.outside_split_rates,
                label=f"split rates {context_msg}",
            )
