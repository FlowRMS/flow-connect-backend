"""Run database migrations for multi-tenant setup."""

import asyncio

from loguru import logger

from app.core.config.settings import Settings
from app.core.container import create_container
from app.core.db.db_provider import create_multitenant_for_migration_controller
from commons.migrations.migrations import MultiTenantMigration


async def run_migration() -> None:
    """Execute database migrations across all tenants."""
    async with create_container().context() as conn_ctx:
        settings = await conn_ctx.resolve(Settings)
        controller = await create_multitenant_for_migration_controller(
            settings.pg_url.unicode_string()
        )
        await MultiTenantMigration(controller, config_file="alembic.ini").run(
            chunk_size=8
        )


def main() -> None:
    """Main entry point for running migrations."""
    logger.info("Running migration")
    asyncio.run(run_migration())
    logger.success("Migration complete")


if __name__ == "__main__":
    main()
