import asyncpg
from loguru import logger


class DatabaseCreationService:
    """
    Service for creating PostgreSQL databases for new tenants.

    Uses asyncpg directly because CREATE DATABASE cannot run inside
    a transaction (SQLAlchemy sessions use transactions by default).
    """

    def __init__(self, pg_url: str) -> None:
        # Convert SQLAlchemy URL format to asyncpg format
        # postgresql+asyncpg://... -> postgresql://...
        url = pg_url.replace("postgresql+asyncpg://", "postgresql://")
        # Ensure sslmode=require for cloud databases (Neon, etc.)
        if "sslmode" not in url and "neon.tech" in url:
            url = f"{url}?sslmode=require"
        self.pg_url = url

    async def _get_connection(self) -> asyncpg.Connection:
        """Get a raw asyncpg connection (not in a transaction)."""
        return await asyncpg.connect(self.pg_url)

    async def database_exists(self, db_name: str) -> bool:
        """Check if a database exists in PostgreSQL."""
        conn = await self._get_connection()
        try:
            result = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname = $1)",
                db_name,
            )
            return bool(result)
        finally:
            await conn.close()

    async def create_database(self, db_name: str) -> None:
        """
        Create a new PostgreSQL database.

        The database name is quoted as an identifier to handle special
        characters (like hyphens) safely.
        """
        # Quote the database name as an identifier to prevent SQL injection
        # and handle special characters like hyphens
        quoted_name = f'"{db_name}"'

        conn = await self._get_connection()
        try:
            logger.info("Creating database", db_name=db_name)
            await conn.execute(f"CREATE DATABASE {quoted_name}")
            logger.info("Database created successfully", db_name=db_name)
        finally:
            await conn.close()
