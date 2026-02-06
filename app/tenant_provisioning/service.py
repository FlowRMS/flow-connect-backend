import re
import unicodedata
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Protocol
from urllib.parse import urlparse, urlunparse

from commons.db.models.tenant import Tenant
from loguru import logger

from app.tenant_provisioning.repository import TenantRepository


class ProvisioningStatus(Enum):
    CREATED = "created"
    ALREADY_EXISTS = "already_exists"
    FAILED = "failed"


@dataclass
class ProvisioningResult:
    status: ProvisioningStatus
    tenant_id: uuid.UUID | None = None
    error: str | None = None


class DatabaseServiceProtocol(Protocol):
    async def database_exists(self, db_name: str) -> bool: ...
    async def create_database(self, db_name: str) -> None: ...


class MigrationServiceProtocol(Protocol):
    async def run_migrations(self, db_url: str) -> str: ...


class TenantProvisioningService:
    def __init__(
        self,
        repository: TenantRepository,
        database_service: DatabaseServiceProtocol,
        migration_service: MigrationServiceProtocol,
        db_connection_url: str,
        db_host: str,
        db_ro_host: str,
        db_username: str,
    ) -> None:
        self.repository = repository
        self.database_service = database_service
        self.migration_service = migration_service
        self.db_connection_url = (
            db_connection_url  # Full URL for building connection strings
        )
        self.db_host = db_host  # Just hostname for tenant record
        self.db_ro_host = db_ro_host  # Read-only hostname for tenant record
        self.db_username = db_username  # Username for tenant record

    async def provision(
        self,
        org_id: str,
        org_name: str,
    ) -> ProvisioningResult:
        """
        Provision a new tenant for an organization.

        Flow:
        1. Check if tenant already exists
        2. Generate unique tenant URL from org name
        3. Create tenant record
        4. Create database if needed
        5. Run migrations
        6. Mark tenant as initialized
        """
        # Check if tenant already exists
        existing = await self.repository.get_by_org_id(org_id)
        if existing:
            logger.info("Tenant already exists", org_id=org_id, tenant_id=existing.id)
            return ProvisioningResult(
                status=ProvisioningStatus.ALREADY_EXISTS,
                tenant_id=existing.id,
            )

        # Generate tenant URL
        tenant_url = await self._generate_unique_url(org_name)
        logger.info("Generated tenant URL", org_id=org_id, tenant_url=tenant_url)

        # Create tenant record
        tenant = Tenant(
            id=uuid.uuid4(),
            org_id=org_id,
            name=org_name,
            url=tenant_url,
            initialize=False,
            database=self.db_host,
            read_only_database=self.db_ro_host,
            username=self.db_username,
            alembic_version="",
        )
        tenant = await self.repository.create(tenant)
        logger.info("Created tenant record", tenant_id=tenant.id)

        # Create database if needed
        if not await self.database_service.database_exists(tenant_url):
            await self.database_service.create_database(tenant_url)
            logger.info("Created database", db_name=tenant_url)

        # Run migrations
        db_url = self._build_db_url(tenant_url)
        alembic_version = await self.migration_service.run_migrations(db_url)
        logger.info("Migrations complete", version=alembic_version)

        # Mark as initialized with alembic version
        await self.repository.update_initialize(
            tenant.id,
            initialize=True,
            alembic_version=alembic_version,
        )
        logger.info("Tenant provisioning complete", tenant_id=tenant.id)

        return ProvisioningResult(
            status=ProvisioningStatus.CREATED,
            tenant_id=tenant.id,
        )

    def _build_db_url(self, db_name: str) -> str:
        """Build a database URL for the given database name, preserving query params."""
        parsed = urlparse(self.db_connection_url)
        # Replace the path (database name) while keeping everything else
        new_parsed = parsed._replace(path=f"/{db_name}")
        url = urlunparse(new_parsed)
        # Ensure sslmode=require for cloud databases (Neon, etc.)
        if "sslmode" not in url and "neon.tech" in url:
            url = f"{url}?sslmode=require"
        return url

    async def _generate_unique_url(self, org_name: str) -> str:
        """Generate a unique tenant URL, appending suffix if needed."""
        base_url = self.generate_tenant_url(org_name)
        url = base_url

        # Check for collisions and append suffix if needed
        suffix = 1
        while await self.repository.get_by_url(url):
            url = f"{base_url}-{suffix}"
            suffix += 1

        return url

    @staticmethod
    def generate_tenant_url(org_name: str) -> str:
        """
        Generate a valid database/tenant URL from organization name.

        Converts to lowercase, removes special characters, replaces spaces
        with hyphens, and ensures the result is a valid identifier.
        """
        # Normalize unicode characters (convert accented chars to ASCII equivalents)
        normalized = unicodedata.normalize("NFKD", org_name)
        ascii_text = normalized.encode("ASCII", "ignore").decode("ASCII")

        # Convert to lowercase
        result = ascii_text.lower()

        # Replace spaces and underscores with hyphens
        result = re.sub(r"[\s_]+", "-", result)

        # Remove any character that isn't alphanumeric or hyphen
        result = re.sub(r"[^a-z0-9-]", "", result)

        # Collapse multiple hyphens into one
        result = re.sub(r"-+", "-", result)

        # Remove leading/trailing hyphens
        result = result.strip("-")

        return result
