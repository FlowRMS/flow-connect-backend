from commons.db.v6.commission.orders import Order
from commons.db.v6.crm import Quote
from commons.db.v6.crm.jobs.jobs_model import Job
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.pre_opportunities.pre_opportunity_model import PreOpportunity
from commons.db.v6.crm.tasks.task_model import Task
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.watchers.processors.watcher_notification_processor import (
    WatcherNotificationProcessor,
)
from app.graphql.watchers.repositories.entity_watcher_repository import (
    EntityWatcherRepository,
)
from app.workers.services.resend_notification_service import ResendNotificationService


class JobWatcherNotificationProcessor(WatcherNotificationProcessor[Job]):
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
            EntityType.JOB,
            "job_name",
        )


class TaskWatcherNotificationProcessor(WatcherNotificationProcessor[Task]):
    def __init__(
        self,
        session: AsyncSession,
        notification_service: ResendNotificationService,
        watcher_repository: EntityWatcherRepository,
    ) -> None:
        super().__init__(
            session, notification_service, watcher_repository, EntityType.TASK, "title"
        )


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


class OrderWatcherNotificationProcessor(WatcherNotificationProcessor[Order]):
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
            EntityType.ORDER,
            "order_number",
        )


class PreOpportunityWatcherNotificationProcessor(
    WatcherNotificationProcessor[PreOpportunity]
):
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
            EntityType.PRE_OPPORTUNITY,
            "entity_number",
        )


__all__ = [
    "WatcherNotificationProcessor",
    "JobWatcherNotificationProcessor",
    "TaskWatcherNotificationProcessor",
    "QuoteWatcherNotificationProcessor",
    "OrderWatcherNotificationProcessor",
    "PreOpportunityWatcherNotificationProcessor",
]
