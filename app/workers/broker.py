"""TaskIQ broker configuration for background tasks."""

from taskiq import InMemoryBroker, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource

# Using InMemoryBroker for simplicity - works well for single-instance deployments
# For production with multiple workers, consider using Redis broker:
# from taskiq_redis import ListQueueBroker
# broker = ListQueueBroker(url="redis://localhost:6379")

broker = InMemoryBroker()

# Create scheduler with label-based source (reads cron config from task decorators)
scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
