from commons.db.v6.crm import Quote
from commons.db.v6.crm.links.entity_type import EntityType
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.watchers.processors.watcher_notification_processor import (
    WatcherNotificationProcessor,
)
from app.graphql.watchers.repositories.entity_watcher_repository import (
    EntityWatcherRepository,
)
from app.workers.services.resend_notification_service import ResendNotificationService


class QuoteWatcherNotificationProcessor(WatcherNotificationProcessor[Quote]):
    def __init__(
        self,
        session: AsyncSession,
        notification_service: ResendNotificationService,
        watcher_repository: EntityWatcherRepository,
    ) -> None:
        super().__init__(
            session,
            notification_service,
            watcher_repository,
            EntityType.QUOTE,
            "quote_number",
        )
