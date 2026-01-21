import argparse
import asyncio
import logging
import uuid
from dataclasses import dataclass
from pathlib import Path

import asyncpg
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

FACTORY_TYPES = {"Principal", "Manufacturer"}
CUSTOMER_TYPES = {"Distributor"}

ADDRESS_SOURCE_TYPE_CUSTOMER = 1
ADDRESS_SOURCE_TYPE_FACTORY = 2
ADDRESS_TYPE_OTHER = 4


@dataclass
class MigrationConfig:
    excel_path: Path
    dest_dsn: str
    created_by_id: uuid.UUID
    dry_run: bool = False


def load_excel_data(excel_path: Path) -> pd.DataFrame:
    logger.info(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)
    df = df.fillna("")
    logger.info(f"Loaded {len(df)} rows with columns: {df.columns.tolist()}")
    return df


def categorize_companies(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    factories = df[df["Type"].isin(FACTORY_TYPES)].copy()
    customers = df[df["Type"].isin(CUSTOMER_TYPES)].copy()
    companies = df[~df["Type"].isin(FACTORY_TYPES | CUSTOMER_TYPES)].copy()

    logger.info(f"Categorized: {len(factories)} factories, {len(customers)} customers, {len(companies)} companies")
    return factories, customers, companies


def build_address_record(
    row: pd.Series,
    source_id: uuid.UUID,
    source_type: int,
) -> tuple | None:
    address = str(row.get("Address", "")).strip()
    city = str(row.get("City", "")).strip()
    country = str(row.get("Country", "")).strip() or "USA"

    if not address or not city:
        return None

    zip_code = str(row.get("Zip Code", "")).strip()
    if not zip_code:
        zip_code = "00000"

    return (
        uuid.uuid4(),
        source_id,
        source_type,
        ADDRESS_TYPE_OTHER,
        address[:255],
        None,
        city[:100],
        str(row.get("State", ""))[:100] if row.get("State") else None,
        zip_code[:20],
        country[:100],
        None,
        True,
    )


async def migrate_factories(
    dest: asyncpg.Connection,
    factories_df: pd.DataFrame,
    created_by_id: uuid.UUID,
    dry_run: bool = False,
) -> tuple[int, list[tuple]]:
    logger.info("Starting factory migration from Excel...")

    if factories_df.empty:
        logger.info("No factories to migrate")
        return 0, []

    records = []
    address_records = []

    for _, row in factories_df.iterrows():
        factory_id = uuid.uuid4()
        records.append((
            factory_id,
            str(row["Company"])[:255] if row["Company"] else "Unknown",
            None,
            None,
            str(row["Phone 1"])[:50] if row["Phone 1"] else None,
            0,
            0,
            0,
            str(row["Comments"]) if row["Comments"] else None,
            None,
            None,
            True,
            0,
            0,
            created_by_id,
        ))

        addr = build_address_record(row, factory_id, ADDRESS_SOURCE_TYPE_FACTORY)
        if addr:
            address_records.append(addr)

    if dry_run:
        logger.info(f"[DRY RUN] Would insert {len(records)} factories, {len(address_records)} addresses")
        return len(records), address_records

    await dest.executemany(
        """
        INSERT INTO pycore.factories (
            id, title, account_number, email, phone,
            base_commission_rate, commission_discount_rate, overall_discount_rate,
            additional_information, freight_terms, external_payment_terms,
            published, freight_discount_type, creation_type, created_by_id,
            created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, now())
        ON CONFLICT (id) DO NOTHING
        """,
        records,
    )

    logger.info(f"Migrated {len(records)} factories")
    return len(records), address_records


async def migrate_customers(
    dest: asyncpg.Connection,
    customers_df: pd.DataFrame,
    created_by_id: uuid.UUID,
    dry_run: bool = False,
) -> tuple[int, list[tuple]]:
    logger.info("Starting customer migration from Excel...")

    if customers_df.empty:
        logger.info("No customers to migrate")
        return 0, []

    parent_id_map: dict[int, uuid.UUID] = {}
    records_no_parent = []
    records_with_parent = []
    address_records = []
    row_data: dict[uuid.UUID, pd.Series] = {}

    for _, row in customers_df.iterrows():
        company_id = int(row["Company Id"]) if row["Company Id"] else 0
        parent_id = int(row["Parent Id"]) if row["Parent Id"] else 0
        new_uuid = uuid.uuid4()
        parent_id_map[company_id] = new_uuid
        row_data[new_uuid] = row

        record = (
            new_uuid,
            str(row["Company"])[:255] if row["Company"] else "Unknown",
            True,
            parent_id == company_id,
            created_by_id,
            company_id,
            parent_id,
        )

        if parent_id == company_id or parent_id == 0:
            records_no_parent.append(record)
        else:
            records_with_parent.append(record)

    for record in records_no_parent + records_with_parent:
        customer_id = record[0]
        row = row_data[customer_id]
        addr = build_address_record(row, customer_id, ADDRESS_SOURCE_TYPE_CUSTOMER)
        if addr:
            address_records.append(addr)

    if dry_run:
        total = len(records_no_parent) + len(records_with_parent)
        logger.info(f"[DRY RUN] Would insert {total} customers, {len(address_records)} addresses")
        return total, address_records

    if records_no_parent:
        await dest.executemany(
            """
            INSERT INTO pycore.customers (
                id, company_name, published, is_parent, created_by_id, created_at
            ) VALUES ($1, $2, $3, $4, $5, now())
            ON CONFLICT (id) DO NOTHING
            """,
            [(r[0], r[1], r[2], r[3], r[4]) for r in records_no_parent],
        )

    if records_with_parent:
        for record in records_with_parent:
            new_id, company_name, published, is_parent, cby_id, company_id, parent_id = record
            parent_uuid = parent_id_map.get(parent_id)
            await dest.execute(
                """
                INSERT INTO pycore.customers (
                    id, company_name, parent_id, published, is_parent, created_by_id, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, now())
                ON CONFLICT (id) DO NOTHING
                """,
                new_id,
                company_name,
                parent_uuid,
                published,
                is_parent,
                cby_id,
            )

    total = len(records_no_parent) + len(records_with_parent)
    logger.info(f"Migrated {total} customers ({len(records_no_parent)} parents, {len(records_with_parent)} children)")
    return total, address_records


async def migrate_companies(
    dest: asyncpg.Connection,
    companies_df: pd.DataFrame,
    created_by_id: uuid.UUID,
    dry_run: bool = False,
) -> int:
    logger.info("Starting company migration from Excel...")

    if companies_df.empty:
        logger.info("No companies to migrate")
        return 0

    parent_id_map: dict[int, uuid.UUID] = {}
    records_no_parent = []
    records_with_parent = []

    for _, row in companies_df.iterrows():
        company_id = int(row["Company Id"]) if row["Company Id"] else 0
        parent_id = int(row["Parent Id"]) if row["Parent Id"] else 0
        new_uuid = uuid.uuid4()
        parent_id_map[company_id] = new_uuid

        record = (
            new_uuid,
            str(row["Company"])[:255] if row["Company"] else "Unknown",
            1,
            str(row["Website"])[:255] if row["Website"] else None,
            str(row["Phone 1"])[:50] if row["Phone 1"] else None,
            None,
            created_by_id,
            company_id,
            parent_id,
        )

        if parent_id == company_id or parent_id == 0:
            records_no_parent.append(record)
        else:
            records_with_parent.append(record)

    if dry_run:
        logger.info(f"[DRY RUN] Would insert {len(records_no_parent) + len(records_with_parent)} companies")
        return len(records_no_parent) + len(records_with_parent)

    if records_no_parent:
        await dest.executemany(
            """
            INSERT INTO pycrm.companies (
                id, name, company_source_type, website, phone, tags,
                parent_company_id, created_by_id, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, NULL, $7, now())
            ON CONFLICT (id) DO NOTHING
            """,
            [(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in records_no_parent],
        )

    if records_with_parent:
        for record in records_with_parent:
            new_id, name, source_type, website, phone, tags, cby_id, company_id, parent_id = record
            parent_uuid = parent_id_map.get(parent_id)
            await dest.execute(
                """
                INSERT INTO pycrm.companies (
                    id, name, company_source_type, website, phone, tags,
                    parent_company_id, created_by_id, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, now())
                ON CONFLICT (id) DO NOTHING
                """,
                new_id,
                name,
                source_type,
                website,
                phone,
                tags,
                parent_uuid,
                cby_id,
            )

    total = len(records_no_parent) + len(records_with_parent)
    logger.info(f"Migrated {total} companies ({len(records_no_parent)} parents, {len(records_with_parent)} children)")
    return total


async def migrate_addresses(
    dest: asyncpg.Connection,
    address_records: list[tuple],
    dry_run: bool = False,
) -> int:
    logger.info("Starting address migration from Excel...")

    if not address_records:
        logger.info("No addresses to migrate")
        return 0

    if dry_run:
        logger.info(f"[DRY RUN] Would insert {len(address_records)} addresses")
        return len(address_records)

    await dest.executemany(
        """
        INSERT INTO pycore.addresses (
            id, source_id, source_type, address_type,
            line_1, line_2, city, state, zip_code, country,
            notes, is_primary, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, now())
        ON CONFLICT (id) DO NOTHING
        """,
        address_records,
    )

    logger.info(f"Migrated {len(address_records)} addresses")
    return len(address_records)


async def run_migration(config: MigrationConfig) -> dict[str, int]:
    logger.info("Starting Excel company migration...")

    df = load_excel_data(config.excel_path)
    factories_df, customers_df, companies_df = categorize_companies(df)

    if config.dry_run:
        logger.info("[DRY RUN] No database changes will be made")
        factory_count, factory_addrs = await migrate_factories(
            None, factories_df, config.created_by_id, dry_run=True  # type: ignore[arg-type]
        )
        customer_count, customer_addrs = await migrate_customers(
            None, customers_df, config.created_by_id, dry_run=True  # type: ignore[arg-type]
        )
        return {
            "factories": factory_count,
            "customers": customer_count,
            "companies": len(companies_df),
            "addresses": len(factory_addrs) + len(customer_addrs),
        }

    dest = await asyncpg.connect(
        config.dest_dsn,
        timeout=60,
        command_timeout=600.0,
        server_settings={
            "statement_timeout": "0",
            "idle_in_transaction_session_timeout": "0",
        },
    )

    results: dict[str, int] = {}
    all_addresses: list[tuple] = []

    try:
        factory_count, factory_addrs = await migrate_factories(
            dest, factories_df, config.created_by_id, config.dry_run
        )
        results["factories"] = factory_count
        all_addresses.extend(factory_addrs)

        customer_count, customer_addrs = await migrate_customers(
            dest, customers_df, config.created_by_id, config.dry_run
        )
        results["customers"] = customer_count
        all_addresses.extend(customer_addrs)

        results["companies"] = await migrate_companies(
            dest, companies_df, config.created_by_id, config.dry_run
        )

        results["addresses"] = await migrate_addresses(dest, all_addresses, config.dry_run)

        logger.info("Migration completed successfully!")
        logger.info(f"Results: {results}")

    except Exception as e:
        logger.exception(f"Migration failed: {e}")
        raise
    finally:
        await dest.close()

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate companies from Excel to Flow v6")
    parser.add_argument(
        "--excel-path",
        required=True,
        help="Path to the Excel file",
    )
    parser.add_argument(
        "--dest-url",
        required=True,
        help="Destination database URL",
    )
    parser.add_argument(
        "--created-by-id",
        required=True,
        help="UUID of the user to set as created_by",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be migrated without making changes",
    )
    args = parser.parse_args()

    config = MigrationConfig(
        excel_path=Path(args.excel_path),
        dest_dsn=args.dest_url,
        created_by_id=uuid.UUID(args.created_by_id),
        dry_run=args.dry_run,
    )

    asyncio.run(run_migration(config))


if __name__ == "__main__":
    main()
