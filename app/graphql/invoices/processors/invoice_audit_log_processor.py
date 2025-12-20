from commons.db.models import Invoice
from loguru import logger

from app.core.processors import (
    BaseProcessor,
    EntityContext,
    RepositoryEvent,
    entity_processor,
)


@entity_processor(Invoice)
class InvoiceAuditLogProcessor(BaseProcessor[Invoice]):
    """Logs audit entries when Invoice is created, updated, or deleted."""

    def __init__(self) -> None:
        super().__init__()

    @property
    def events(self) -> list[RepositoryEvent]:
        return [
            RepositoryEvent.POST_CREATE,
            RepositoryEvent.POST_UPDATE,
            RepositoryEvent.POST_DELETE,
        ]

    async def process(self, context: EntityContext[Invoice]) -> None:
        action = context.event.value.replace("post_", "")

        if context.original_entity and context.event == RepositoryEvent.POST_UPDATE:
            logger.info(
                f"Invoice {context.entity_id} updated: "
                f"number={context.entity.invoice_number}, "
                f"original_number={context.original_entity.invoice_number}"
            )
        else:
            logger.info(
                f"Invoice {context.entity_id} {action}: "
                f"number={context.entity.invoice_number}"
            )
