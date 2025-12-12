"""TaskIQ broker configuration for background tasks."""

import os

from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import RedisStreamBroker

from app.core.db.models import configure_mappers

configure_mappers()

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")

broker = RedisStreamBroker(url=REDIS_URL)

# Create scheduler with label-based source (reads cron config from task decorators)
scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
