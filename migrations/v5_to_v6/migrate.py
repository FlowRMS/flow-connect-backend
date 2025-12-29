import asyncio
import logging
from dataclasses import dataclass

import asyncpg

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class MigrationConfig:
    source_dsn: str
    dest_dsn: str
    batch_size: int = 500


async def migrate_users(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate users from v5 (user.users) to v6 (pyuser.users)."""
    logger.info("Starting user migration...")

    users = await source.fetch("""
        SELECT
            u.id,
            u.username,
            u.first_name,
            u.last_name,
            u.email,
            u.keycloak_id::text as auth_provider_id,
            CASE
                WHEN ur.name = 'admin' THEN 1
                WHEN ur.name = 'manager' THEN 2
                WHEN ur.name = 'sales_rep' THEN 3
                ELSE 4
            END AS role,
            u.enabled,
            COALESCE(u.inside, false) as inside,
            COALESCE(u.outside, false) as outside,
            COALESCE(u.entry_date, now()) as created_at
        FROM "user".users u
        LEFT JOIN "user".user_roles ur ON u.role_id = ur.id
    """)

    if not users:
        logger.info("No users to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pyuser.users (
            id, username, first_name, last_name, email,
            auth_provider_id, role, enabled, inside, outside, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
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
        [(
            u["id"],
            u["username"],
            u["first_name"],
            u["last_name"],
            u["email"],
            u["auth_provider_id"],
            u["role"],
            u["enabled"],
            u["inside"],
            u["outside"],
            u["created_at"],
        ) for u in users],
    )

    logger.info(f"Migrated {len(users)} users")
    return len(users)


async def migrate_customers(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate customers from v5 (core.customers) to v6 (pycore.customers)."""
    logger.info("Starting customer migration...")

    # First, get customers without parents
    parent_customers = await source.fetch("""
        SELECT
            c.id,
            c.company_name,
            c.published,
            c.is_parent,
            c.created_by as created_by_id,
            COALESCE(c.entry_date, now()) as created_at
        FROM core.customers c
        WHERE c.parent_id IS NULL
    """)

    # Insert parent customers first
    if parent_customers:
        await dest.executemany(
            """
            INSERT INTO pycore.customers (
                id, company_name, parent_id, published, is_parent, created_by_id, created_at
            ) VALUES ($1, $2, NULL, $3, $4, $5, $6)
            ON CONFLICT (id) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                published = EXCLUDED.published,
                is_parent = EXCLUDED.is_parent
            """,
            [(
                c["id"],
                c["company_name"],
                c["published"],
                c["is_parent"],
                c["created_by_id"],
                c["created_at"],
            ) for c in parent_customers],
        )

    # Then get and insert child customers
    child_customers = await source.fetch("""
        SELECT
            c.id,
            c.company_name,
            c.parent_id,
            c.published,
            c.is_parent,
            c.created_by as created_by_id,
            COALESCE(c.entry_date, now()) as created_at
        FROM core.customers c
        WHERE c.parent_id IS NOT NULL
    """)

    if child_customers:
        await dest.executemany(
            """
            INSERT INTO pycore.customers (
                id, company_name, parent_id, published, is_parent, created_by_id, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO UPDATE SET
                company_name = EXCLUDED.company_name,
                parent_id = EXCLUDED.parent_id,
                published = EXCLUDED.published,
                is_parent = EXCLUDED.is_parent
            """,
            [(
                c["id"],
                c["company_name"],
                c["parent_id"],
                c["published"],
                c["is_parent"],
                c["created_by_id"],
                c["created_at"],
            ) for c in child_customers],
        )

    total = len(parent_customers) + len(child_customers)
    logger.info(f"Migrated {total} customers ({len(parent_customers)} parents, {len(child_customers)} children)")
    return total


async def migrate_factories(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    """Migrate factories from v5 (core.factories) to v6 (pycore.factories)."""
    logger.info("Starting factory migration...")

    factories = await source.fetch(r"""
        SELECT
            f.id,
            f.title,
            f.account_number,
            f.email,
            f.phone,
            CASE
                WHEN f.lead_time ~ '^\d+$' THEN f.lead_time::integer
                ELSE NULL
            END AS lead_time,
            CASE
                WHEN f.payment_terms ~ '^\d+$' THEN f.payment_terms::integer
                ELSE NULL
            END AS payment_terms,
            COALESCE(f.commission_rate, 0) as base_commission_rate,
            COALESCE(f.commission_discount_rate, 0) as commission_discount_rate,
            COALESCE(f.overall_discount_rate, 0) as overall_discount_rate,
            f.additional_information,
            f.freight_terms,
            f.external_payment_terms,
            f.published,
            f.freight_discount_type,
            f.creation_type,
            f.created_by as created_by_id,
            COALESCE(f.entry_date, now()) as created_at
        FROM core.factories f
    """)

    if not factories:
        logger.info("No factories to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycore.factories (
            id, title, account_number, email, phone, logo_id,
            lead_time, payment_terms, base_commission_rate,
            commission_discount_rate, overall_discount_rate,
            additional_information, freight_terms, external_payment_terms,
            published, freight_discount_type, creation_type,
            created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, NULL, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            account_number = EXCLUDED.account_number,
            email = EXCLUDED.email,
            phone = EXCLUDED.phone,
            lead_time = EXCLUDED.lead_time,
            payment_terms = EXCLUDED.payment_terms,
            base_commission_rate = EXCLUDED.base_commission_rate,
            commission_discount_rate = EXCLUDED.commission_discount_rate,
            overall_discount_rate = EXCLUDED.overall_discount_rate,
            additional_information = EXCLUDED.additional_information,
            freight_terms = EXCLUDED.freight_terms,
            external_payment_terms = EXCLUDED.external_payment_terms,
            published = EXCLUDED.published,
            freight_discount_type = EXCLUDED.freight_discount_type,
            creation_type = EXCLUDED.creation_type
        """,
        [(
            f["id"],
            f["title"],
            f["account_number"],
            f["email"],
            f["phone"],
            f["lead_time"],
            f["payment_terms"],
            f["base_commission_rate"],
            f["commission_discount_rate"],
            f["overall_discount_rate"],
            f["additional_information"],
            f["freight_terms"],
            f["external_payment_terms"],
            f["published"],
            f["freight_discount_type"],
            f["creation_type"],
            f["created_by_id"],
            f["created_at"],
        ) for f in factories],
    )

    logger.info(f"Migrated {len(factories)} factories")
    return len(factories)


async def run_migration(config: MigrationConfig) -> dict[str, int]:
    """Run full migration from v5 to v6."""
    logger.info("Connecting to databases...")

    source = await asyncpg.connect(config.source_dsn)
    dest = await asyncpg.connect(config.dest_dsn)

    results: dict[str, int] = {}

    try:
        # Order matters due to foreign key dependencies
        results["users"] = await migrate_users(source, dest)
        results["customers"] = await migrate_customers(source, dest)
        results["factories"] = await migrate_factories(source, dest)

        logger.info("Migration completed successfully!")
        logger.info(f"Results: {results}")

    except Exception as e:
        logger.exception(f"Migration failed: {e}")
        raise
    finally:
        await source.close()
        await dest.close()

    return results


async def run_migration_for_tenant(
    tenant: str,
    source_base_url: str,
    dest_base_url: str,
) -> dict[str, int]:
    """Run migration for a specific tenant."""
    config = MigrationConfig(
        source_dsn=f"{source_base_url}/{tenant}",
        dest_dsn=f"{dest_base_url}/{tenant}",
    )
    logger.info(f"Running migration for tenant: {tenant}")
    return await run_migration(config)


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Migrate data from v5 to v6")
    _ = parser.add_argument("--tenant", required=True, help="Tenant name to migrate")
    _ = parser.add_argument(
        "--source-url",
        default=os.environ.get("V5_DATABASE_URL"),
        help="Source database base URL (without tenant)",
    )
    _ = parser.add_argument(
        "--dest-url",
        default=os.environ.get("V6_DATABASE_URL"),
        help="Destination database base URL (without tenant)",
    )
    _ = parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be migrated without making changes",
    )
    args = parser.parse_args()

    if not args.source_url or not args.dest_url:
        parser.error("--source-url and --dest-url are required (or set V5_DATABASE_URL and V6_DATABASE_URL)")

    _ = asyncio.run(run_migration_for_tenant(
        tenant=args.tenant,
        source_base_url=args.source_url,
        dest_base_url=args.dest_url,
    ))
