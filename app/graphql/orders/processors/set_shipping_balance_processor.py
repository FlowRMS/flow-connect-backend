from commons.db.v6.commission.orders import Order

from app.core.processors import BaseProcessor, EntityContext, RepositoryEvent


class SetShippingBalanceProcessor(BaseProcessor[Order]):
    def __init__(self) -> None:
        super().__init__()

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Order]) -> None:
        order = context.entity

        for detail in order.details:
            detail.shipping_balance = detail.total - detail.shipping_balance
