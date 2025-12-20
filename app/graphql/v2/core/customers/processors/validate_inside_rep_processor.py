from loguru import logger

from app.core.processors import (
    BaseProcessor,
    EntityContext,
    RepositoryEvent,
    entity_processor,
)
from app.graphql.v2.core.customers.models.customer import CustomerV2


@entity_processor(CustomerV2)
class ValidateInsideRepProcessor(BaseProcessor[CustomerV2]):
    """Sets inside_rep_id to created_by_id if not provided."""

    def __init__(self) -> None:
        super().__init__()

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[CustomerV2]) -> None:
        logger.info("Validating inside_rep_id for CustomerV2")
        customer = context.entity

        if not customer.inside_rep_id:
            raise ValueError("inside_rep_id must be provided for CustomerV2")
