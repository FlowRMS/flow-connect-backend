from commons.migrations.alembic_helpers import Alembic, get_current_revision
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config.settings import Settings


class TenantMigrationService:
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings
        self.config_file = "alembic.ini"

    async def run_migrations(self, db_name: str) -> str:
        database_url = (
            self.settings.pg_url.unicode_string().rsplit("/", 1)[0] + f"/{db_name}"
        )
        engine: AsyncEngine = create_async_engine(database_url)

        try:
            logger.info(f"Running migrations for database: {db_name}")
            alembic = Alembic(engine, self.config_file)
            alembic.upgrade_database()

            current_rev = get_current_revision(self.config_file) or ""
            logger.info(f"Migrations complete for {db_name}, revision: {current_rev}")
            return current_rev
        finally:
            await engine.dispose()

    def get_current_revision(self) -> str:
        return get_current_revision(self.config_file) or ""
