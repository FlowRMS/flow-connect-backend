from app.graphql.watchers.processors.job_watcher_notification_processor import (
    JobWatcherNotificationProcessor,
)
from app.graphql.watchers.processors.order_watcher_notification_processor import (
    OrderWatcherNotificationProcessor,
)
from app.graphql.watchers.processors.pre_opportunity_watcher_notification_processor import (
    PreOpportunityWatcherNotificationProcessor,
)
from app.graphql.watchers.processors.quote_watcher_notification_processor import (
    QuoteWatcherNotificationProcessor,
)
from app.graphql.watchers.processors.task_watcher_notification_processor import (
    TaskWatcherNotificationProcessor,
)
from app.graphql.watchers.processors.watcher_notification_processor import (
    WatcherNotificationProcessor,
)

__all__ = [
    "WatcherNotificationProcessor",
    "JobWatcherNotificationProcessor",
    "TaskWatcherNotificationProcessor",
    "QuoteWatcherNotificationProcessor",
    "OrderWatcherNotificationProcessor",
    "PreOpportunityWatcherNotificationProcessor",
]
