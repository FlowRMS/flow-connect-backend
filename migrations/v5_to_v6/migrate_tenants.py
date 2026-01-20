import asyncio
import logging
import re
import uuid
from dataclasses import dataclass, field

import asyncpg
from workos import AsyncWorkOSClient

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class V5Tenant:
    name: str
    url: str
    database: str


@dataclass
class V5User:
    id: uuid.UUID
    username: str
    first_name: str | None
    last_name: str | None
    email: str
    keycloak_id: str | None
    role: str
    enabled: bool
    inside: bool
    outside: bool


@dataclass
class MigrationConfig:
    v5_master_dsn: str
    v5_base_url: str
    v6_base_url: str
    workos_api_key: str
    workos_client_id: str
    dry_run: bool = False
    skip_existing: bool = True


@dataclass
class TenantMigrationResult:
    tenant_name: str
    success: bool
    workos_org_id: str | None = None
    db_created: bool = False
    users_migrated: int = 0
    users_synced_to_workos: int = 0
    error: str | None = None


@dataclass
class MigrationSummary:
    tenants_processed: int = 0
    tenants_succeeded: int = 0
    tenants_failed: int = 0
    total_users_migrated: int = 0
    total_users_synced: int = 0
    results: list[TenantMigrationResult] = field(default_factory=list)


def generate_url_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def map_role_to_rbac(role_name: str) -> str:
    role_mapping = {
        "admin": "administrator",
        "manager": "manager",
        "sales_rep": "sales_rep",
    }
    return role_mapping.get(role_name.lower(), "sales_rep")


async def fetch_v5_tenants(master_conn: asyncpg.Connection) -> list[V5Tenant]:
    rows = await master_conn.fetch("""
        SELECT name, url, database
        FROM public.tenants
        WHERE initialize = true
        ORDER BY name
    """)
    return [
        V5Tenant(name=row["name"], url=row["url"], database=row["database"])
        for row in rows
    ]


async def fetch_v5_users(tenant_conn: asyncpg.Connection) -> list[V5User]:
    rows = await tenant_conn.fetch("""
        SELECT
            u.id,
            u.username,
            u.first_name,
            u.last_name,
            u.email,
            u.keycloak_id::text as keycloak_id,
            COALESCE(ur.name, 'sales_rep') as role,
            u.enabled,
            COALESCE(u.inside, false) as inside,
            COALESCE(u.outside, false) as outside
        FROM "user".users u
        LEFT JOIN "user".user_roles ur ON u.role_id = ur.id
    """)
    return [
        V5User(
            id=row["id"],
            username=row["username"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            email=row["email"],
            keycloak_id=row["keycloak_id"],
            role=row["role"],
            enabled=row["enabled"],
            inside=row["inside"],
            outside=row["outside"],
        )
        for row in rows
    ]


async def database_exists(conn: asyncpg.Connection, db_name: str) -> bool:
    result = await conn.fetchval(
        "SELECT 1 FROM pg_database WHERE datname = $1", db_name
    )
    return result is not None


async def create_database(conn: asyncpg.Connection, db_name: str) -> None:
    _ = await conn.execute(f'CREATE DATABASE "{db_name}"')


async def run_migrations(db_url: str) -> str:
    from commons.migrations.alembic_helpers import Alembic, get_current_revision
    from sqlalchemy.ext.asyncio import create_async_engine

    config_file = "alembic.ini"
    engine = create_async_engine(db_url)
    try:
        alembic = Alembic(engine, config_file)
        alembic.upgrade_database()
        return get_current_revision(config_file) or ""
    finally:
        await engine.dispose()


async def find_or_create_workos_org(
    client: AsyncWorkOSClient, tenant_name: str
) -> str | None:
    orgs = await client.organizations.list_organizations()
    for org in orgs.data:
        if org.name == tenant_name:
            logger.info(f"Found existing WorkOS org for {tenant_name}: {org.id}")
            return org.id

    try:
        org = await client.organizations.create_organization(name=tenant_name)
        logger.info(f"Created WorkOS org for {tenant_name}: {org.id}")
        return org.id
    except Exception as e:
        logger.error(f"Failed to create WorkOS org for {tenant_name}: {e}")
        return None


async def find_workos_user_by_email(
    client: AsyncWorkOSClient, email: str
) -> tuple[str, uuid.UUID | None] | None:
    users = await client.user_management.list_users(email=email, limit=1)
    if users.data:
        workos_user = users.data[0]
        external_id = (
            uuid.UUID(workos_user.external_id) if workos_user.external_id else None
        )
        return (workos_user.id, external_id)
    return None


async def create_workos_user(
    client: AsyncWorkOSClient,
    user: V5User,
    org_id: str,
) -> tuple[str, uuid.UUID] | None:
    try:
        workos_user = await client.user_management.create_user(
            email=user.email,
            first_name=user.first_name or user.username,
            last_name=user.last_name or "",
            email_verified=True,
            external_id=str(user.id),
        )
        role_slug = map_role_to_rbac(user.role)
        _ = await client.user_management.create_organization_membership(
            user_id=workos_user.id,
            organization_id=org_id,
            role_slug=role_slug,
        )
        return (workos_user.id, user.id)
    except Exception as e:
        logger.error(f"Failed to create WorkOS user for {user.email}: {e}")
        return None


async def link_workos_user_to_org(
    client: AsyncWorkOSClient,
    workos_user_id: str,
    org_id: str,
    role: str,
) -> bool:
    try:
        memberships = await client.user_management.list_organization_memberships(
            user_id=workos_user_id, organization_id=org_id, limit=1
        )
        if memberships.data:
            return True

        role_slug = map_role_to_rbac(role)
        _ = await client.user_management.create_organization_membership(
            user_id=workos_user_id,
            organization_id=org_id,
            role_slug=role_slug,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to link user {workos_user_id} to org: {e}")
        return False


async def migrate_users_to_v6(
    v5_users: list[V5User],
    dest_conn: asyncpg.Connection,
    workos_client: AsyncWorkOSClient,
    workos_org_id: str,
    dry_run: bool = False,
) -> tuple[int, int]:
    users_migrated = 0
    users_synced = 0

    for user in v5_users:
        workos_user_id: str | None = None

        existing = await find_workos_user_by_email(workos_client, user.email)
        if existing:
            workos_user_id, _ = existing
            linked = await link_workos_user_to_org(
                workos_client, workos_user_id, workos_org_id, user.role
            )
            if linked:
                users_synced += 1
        else:
            if not dry_run:
                created = await create_workos_user(workos_client, user, workos_org_id)
                if created:
                    workos_user_id, _ = created
                    users_synced += 1

        if dry_run:
            logger.info(f"[DRY RUN] Would migrate user: {user.email}")
            continue

        role_int = {"admin": 1, "manager": 2, "sales_rep": 3}.get(
            user.role.lower(), 3
        )
        _ = await dest_conn.execute(
            """
            INSERT INTO pyuser.users (
                id, username, first_name, last_name, email,
                auth_provider_id, role, enabled, inside, outside, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, now())
            ON CONFLICT (id) DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                email = EXCLUDED.email,
                auth_provider_id = EXCLUDED.auth_provider_id,
                role = EXCLUDED.role,
                enabled = EXCLUDED.enabled,
                inside = EXCLUDED.inside,
                outside = EXCLUDED.outside
            """,
            user.id,
            user.username,
            user.first_name,
            user.last_name,
            user.email,
            workos_user_id,
            role_int,
            user.enabled,
            user.inside,
            user.outside,
        )
        users_migrated += 1

    return users_migrated, users_synced


async def migrate_single_tenant(
    tenant: V5Tenant,
    config: MigrationConfig,
    v6_master_conn: asyncpg.Connection,
    workos_client: AsyncWorkOSClient,
) -> TenantMigrationResult:
    result = TenantMigrationResult(tenant_name=tenant.name, success=False)
    url_slug = generate_url_slug(tenant.name)

    try:
        if await database_exists(v6_master_conn, url_slug):
            if config.skip_existing:
                logger.info(f"Database {url_slug} exists, skipping...")
                result.success = True
                result.db_created = False
                return result
            logger.warning(f"Database {url_slug} already exists")
        else:
            if not config.dry_run:
                await create_database(v6_master_conn, url_slug)
                result.db_created = True
                logger.info(f"Created database: {url_slug}")

                v6_db_url = f"{config.v6_base_url}/{url_slug}"
                alembic_rev = await run_migrations(v6_db_url)
                logger.info(f"Migrations complete, revision: {alembic_rev}")
            else:
                logger.info(f"[DRY RUN] Would create database: {url_slug}")
                result.db_created = True

        workos_org_id = await find_or_create_workos_org(workos_client, tenant.name)
        if not workos_org_id:
            result.error = "Failed to create/find WorkOS organization"
            return result
        result.workos_org_id = workos_org_id

        v5_tenant_dsn = f"{config.v5_base_url}/{tenant.url}"
        v5_tenant_conn = await asyncpg.connect(v5_tenant_dsn, timeout=60)
        try:
            v5_users = await fetch_v5_users(v5_tenant_conn)
            logger.info(f"Found {len(v5_users)} users in {tenant.name}")
        finally:
            await v5_tenant_conn.close()

        if config.dry_run:
            for user in v5_users:
                logger.info(f"[DRY RUN] Would migrate user: {user.email}")
            result.users_migrated = len(v5_users)
            result.users_synced_to_workos = len(v5_users)
            result.success = True
            return result

        v6_tenant_dsn = f"{config.v6_base_url}/{url_slug}"
        v6_tenant_conn = await asyncpg.connect(v6_tenant_dsn, timeout=60)
        try:
            migrated, synced = await migrate_users_to_v6(
                v5_users, v6_tenant_conn, workos_client, workos_org_id, config.dry_run
            )
            result.users_migrated = migrated
            result.users_synced_to_workos = synced
        finally:
            await v6_tenant_conn.close()

        result.success = True
        logger.info(
            f"Tenant {tenant.name}: {result.users_migrated} users migrated, "
            f"{result.users_synced_to_workos} synced to WorkOS"
        )

    except Exception as e:
        logger.exception(f"Error migrating tenant {tenant.name}: {e}")
        result.error = str(e)

    return result


async def run_migration(config: MigrationConfig) -> MigrationSummary:
    summary = MigrationSummary()

    workos_client = AsyncWorkOSClient(
        api_key=config.workos_api_key,
        client_id=config.workos_client_id,
    )

    v5_master_conn = await asyncpg.connect(config.v5_master_dsn, timeout=60)
    v6_base_dsn = config.v6_base_url.rsplit("/", 1)[0] + "/postgres"
    v6_master_conn = await asyncpg.connect(v6_base_dsn, timeout=60)

    try:
        tenants = await fetch_v5_tenants(v5_master_conn)
        logger.info(f"Found {len(tenants)} tenants to migrate")

        for tenant in tenants:
            logger.info(f"Processing tenant: {tenant.name}")
            result = await migrate_single_tenant(
                tenant, config, v6_master_conn, workos_client
            )
            summary.results.append(result)
            summary.tenants_processed += 1

            if result.success:
                summary.tenants_succeeded += 1
                summary.total_users_migrated += result.users_migrated
                summary.total_users_synced += result.users_synced_to_workos
            else:
                summary.tenants_failed += 1

    finally:
        await v5_master_conn.close()
        await v6_master_conn.close()

    return summary


def print_summary(summary: MigrationSummary) -> None:
    logger.info("=" * 60)
    logger.info("MIGRATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Tenants processed: {summary.tenants_processed}")
    logger.info(f"Tenants succeeded: {summary.tenants_succeeded}")
    logger.info(f"Tenants failed: {summary.tenants_failed}")
    logger.info(f"Total users migrated: {summary.total_users_migrated}")
    logger.info(f"Total users synced to WorkOS: {summary.total_users_synced}")
    logger.info("=" * 60)

    if summary.tenants_failed > 0:
        logger.info("FAILED TENANTS:")
        for result in summary.results:
            if not result.success:
                logger.error(f"  - {result.tenant_name}: {result.error}")


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description="Migrate tenants from v5 to v6 with WorkOS integration"
    )
    _ = parser.add_argument(
        "--v5-master-dsn",
        default=os.environ.get("V5_MASTER_DSN"),
        help="V5 master database DSN (with public.tenants table)",
    )
    _ = parser.add_argument(
        "--v5-base-url",
        default=os.environ.get("V5_DATABASE_URL"),
        help="V5 database base URL (without tenant name)",
    )
    _ = parser.add_argument(
        "--v6-base-url",
        default=os.environ.get("V6_DATABASE_URL"),
        help="V6 database base URL (without tenant name)",
    )
    _ = parser.add_argument(
        "--workos-api-key",
        default=os.environ.get("WORKOS_API_KEY"),
        help="WorkOS API key",
    )
    _ = parser.add_argument(
        "--workos-client-id",
        default=os.environ.get("WORKOS_CLIENT_ID"),
        help="WorkOS client ID",
    )
    _ = parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making changes",
    )
    _ = parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Don't skip tenants with existing databases",
    )
    args = parser.parse_args()

    if not args.v5_master_dsn:
        parser.error("--v5-master-dsn is required (or set V5_MASTER_DSN)")
    if not args.v5_base_url:
        parser.error("--v5-base-url is required (or set V5_DATABASE_URL)")
    if not args.v6_base_url:
        parser.error("--v6-base-url is required (or set V6_DATABASE_URL)")
    if not args.workos_api_key:
        parser.error("--workos-api-key is required (or set WORKOS_API_KEY)")
    if not args.workos_client_id:
        parser.error("--workos-client-id is required (or set WORKOS_CLIENT_ID)")

    migration_config = MigrationConfig(
        v5_master_dsn=args.v5_master_dsn,
        v5_base_url=args.v5_base_url,
        v6_base_url=args.v6_base_url,
        workos_api_key=args.workos_api_key,
        workos_client_id=args.workos_client_id,
        dry_run=args.dry_run,
        skip_existing=not args.no_skip_existing,
    )

    if args.dry_run:
        logger.info("DRY RUN MODE - no changes will be made")

    migration_summary = asyncio.run(run_migration(migration_config))
    print_summary(migration_summary)
