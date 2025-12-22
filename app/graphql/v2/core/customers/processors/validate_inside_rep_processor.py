from commons.auth import AuthInfo
from commons.db.v6 import Customer
from loguru import logger

from app.core.processors import (
    BaseProcessor,
    EntityContext,
    RepositoryEvent,
    entity_processor,
)


@entity_processor(Customer)
class ValidateInsideRepProcessor(BaseProcessor[Customer]):
    """Sets inside_rep_id to created_by_id if not provided."""

    def __init__(self, auth_info: AuthInfo) -> None:
        super().__init__()
        self.auth_info = auth_info

    @property
    def events(self) -> list[RepositoryEvent]:
        return [RepositoryEvent.PRE_CREATE, RepositoryEvent.PRE_UPDATE]

    async def process(self, context: EntityContext[Customer]) -> None:
        logger.info("Validating inside_rep_id for Customer")
