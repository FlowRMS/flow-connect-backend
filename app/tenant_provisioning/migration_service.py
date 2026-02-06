import asyncio

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from loguru import logger
from sqlalchemy import create_engine

from alembic import command


class MigrationService:
    """
    Service for running Alembic migrations on tenant databases.

    Uses Alembic's programmatic API to apply migrations to individual
    tenant databases.
    """

    def __init__(self, alembic_config_path: str = "alembic.ini") -> None:
        self.alembic_config_path = alembic_config_path

    def _get_alembic_config(self, db_url: str) -> Config:
        """Create Alembic config with the target database URL."""
        config = Config(self.alembic_config_path)
        config.set_main_option("sqlalchemy.url", db_url)
        return config

    async def get_current_revision(self, db_url: str) -> str | None:
        """
        Get the current migration revision for a database.

        Returns None if the database has no migrations applied.
        """
        return await asyncio.to_thread(self._get_current_revision_sync, db_url)

    @staticmethod
    def _get_current_revision_sync(db_url: str) -> str | None:
        """Synchronous implementation of get_current_revision."""
        engine = create_engine(db_url)
        try:
            with engine.connect() as conn:
                context = MigrationContext.configure(
                    conn,
                    opts={"version_table_schema": "connect"},
                )
                return context.get_current_revision()
        finally:
            engine.dispose()

    async def run_migrations(self, db_url: str) -> str:
        """
        Run all pending migrations on the target database.

        Returns the new revision after migrations are applied.
        """
        logger.info("Running migrations", db_url=db_url.split("@")[-1])

        await asyncio.to_thread(self._run_migrations_sync, db_url)

        # Get the new revision
        new_revision = await self.get_current_revision(db_url)
        logger.info("Migrations complete", revision=new_revision)

        return new_revision or ""

    def _run_migrations_sync(self, db_url: str) -> None:
        """Synchronous implementation of run_migrations."""
        config = self._get_alembic_config(db_url)
        command.upgrade(config, "head")
