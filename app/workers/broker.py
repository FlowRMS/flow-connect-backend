"""TaskIQ broker configuration for background tasks."""

from taskiq import InMemoryBroker

# Using InMemoryBroker for simplicity - works well for single-instance deployments
# For production with multiple workers, consider using Redis broker:
# from taskiq_redis import ListQueueBroker
# broker = ListQueueBroker(url="redis://localhost:6379")

broker = InMemoryBroker()
