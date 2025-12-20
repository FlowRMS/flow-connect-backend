from loguru import logger

from app.core.processors import (
    BaseProcessor,
    EntityContext,
    RepositoryEvent,
    entity_processor,
)
from app.graphql.v2.core.customers.models.customer import CustomerV2
from commons.auth import AuthInfo

@entity_processor(CustomerV2)
class ValidateInsideRepProcessor(BaseProcessor[CustomerV2]):
    """Sets inside_rep_id to created_by_id if not provided."""

    def __init__(self, auth_info: AuthInfo) -> None:
        super().__init__()
        self.auth_info = auth_info

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[CustomerV2]) -> None:
        logger.info("Validating inside_rep_id for CustomerV2")
