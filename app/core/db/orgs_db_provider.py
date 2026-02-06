import contextlib
import os
from collections.abc import AsyncIterator, Iterable
from pathlib import Path
from typing import Any

import aioinject
import dotenv
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config.settings import Settings

# Load environment files before checking ORGS_DB_URL
# Use absolute paths to handle different working directories
_project_root = Path(__file__).parent.parent.parent.parent
for env_file in [".env", ".env.local", ".env.dev"]:
    dotenv.load_dotenv(_project_root / env_file, override=False)


class OrgsDbEngine:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine
        self.session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.session_factory() as session:
            yield session


def create_orgs_db_engine(settings: Settings) -> OrgsDbEngine:
    engine = create_async_engine(
        settings.orgs_db_url.unicode_string(),  # pyright: ignore[reportOptionalMemberAccess]
        poolclass=NullPool,
        echo=settings.log_level == "DEBUG",
    )
    return OrgsDbEngine(engine)


@contextlib.asynccontextmanager
async def create_orgs_session(
    orgs_db_engine: OrgsDbEngine,
) -> AsyncIterator[AsyncSession]:
    async with orgs_db_engine.session() as session:
        yield session


# Only register providers if ORGS_DB_URL is configured
# If not configured, ManufacturerService won't be resolvable and will be None
providers: Iterable[aioinject.Provider[Any]] = []
if os.environ.get("ORGS_DB_URL"):
    providers = [
        aioinject.Singleton(create_orgs_db_engine),
        aioinject.Scoped(create_orgs_session),
    ]
