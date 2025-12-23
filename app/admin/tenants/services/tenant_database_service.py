from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config.settings import Settings


class TenantDatabaseService:
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings
        self.engine = create_async_engine(self.settings.pg_url.unicode_string())

    async def database_exists(self, db_name: str) -> bool:
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(
                    text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
                )
                return result.scalar() is not None
        except Exception as e:
            logger.error(f"Error checking database existence: {e}")
            return False

    async def create_database(self, db_name: str) -> None:
        async with self.engine.connect() as conn:
            _ = await conn.execution_options(isolation_level="AUTOCOMMIT")
            _ = await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
        logger.info(f"Created database: {db_name}")

    async def setup_tenant_database(self, db_name: str) -> None:
        if await self.database_exists(db_name):
            raise ValueError(f"Database '{db_name}' already exists")

        await self.create_database(db_name)
