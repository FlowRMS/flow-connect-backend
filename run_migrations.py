"""Run database migrations for multi-tenant setup."""

import asyncio

from loguru import logger

from app.core.config.base_settings import load_dotenv_once
from app.core.config.settings import Settings
from app.core.container import create_container
from app.core.db.db_provider import create_multitenant_for_migration_controller
from commons.migrations.migrations import MultiTenantMigration


async def run_migration() -> None:
    """Execute database migrations across all tenants."""
    async with create_container().context() as conn_ctx:
        settings = await conn_ctx.resolve(Settings)
        controller = await create_multitenant_for_migration_controller(
            settings.pg_url.unicode_string(), settings.environment
        )
        await MultiTenantMigration(controller, config_file="alembic.ini").run(
            chunk_size=2
        )

# downgrades the migration
async def downgrade_migration() -> None:
    async with create_container().context() as conn_ctx:
        settings = await conn_ctx.resolve(Settings)
        controller = await create_multitenant_for_migration_controller(
            settings.pg_url.unicode_string(), settings.environment
        )
        await MultiTenantMigration(controller, config_file="alembic.ini").downgrade()

def main() -> None:
    import argparse
    
    parser = argparse.ArgumentParser()
    _ = parser.add_argument(
        "--env",
        type=str,
        default="dev",
        help="The environment to run the app in (e.g., dev, staging, prod).",
    )
    
    
    """Main entry point for running migrations."""
    _ = parser.add_argument(
        "--downgrade",
        action="store_true",
        help="Downgrade the migration",
    )
    args = parser.parse_args()
    _ = load_dotenv_once(f".env.{args.env}")
    if args.downgrade:
        logger.info("Downgrading migration")
        asyncio.run(downgrade_migration())
        return
    logger.info("Running migration")
    asyncio.run(run_migration())
    logger.success("Migration complete")


if __name__ == "__main__":
    main()
