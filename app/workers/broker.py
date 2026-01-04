from taskiq import TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import RedisStreamBroker

from app.core.config.base_settings import get_settings
from app.core.config.settings import Settings
from app.core.db.models import configure_mappers

configure_mappers()

settings = get_settings(Settings)

broker = RedisStreamBroker(url=settings.redis_url.unicode_string())

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
