import argparse
import asyncio
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import asyncpg
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

ENTITY_TYPE_TASK = 2
ENTITY_TYPE_CONTACT = 3
ENTITY_TYPE_COMPANY = 4
ENTITY_TYPE_NOTE = 5
ENTITY_TYPE_FACTORY = 11
ENTITY_TYPE_CUSTOMER = 12

TASK_STATUS_COMPLETED = 3
TASK_PRIORITY_NORMAL = 2


@dataclass
class MigrationConfig:
    excel_path: Path
    dest_dsn: str
    created_by_id: uuid.UUID
    dry_run: bool = False


@dataclass
class ActivityRecord:
    task_id: uuid.UUID
    note_id: uuid.UUID | None
    contact_ids: list[uuid.UUID]
    customer_id: int | None
    manufacturer_id: int | None
    company_type: str | None


def load_excel_data(excel_path: Path) -> pd.DataFrame:
    logger.info(f"Loading Excel file: {excel_path}")
    df = pd.read_excel(excel_path)
    df = df.fillna("")
    logger.info(f"Loaded {len(df)} rows")
    return df


def parse_attendees(attendees_str: str) -> list[str]:
    if not attendees_str or pd.isna(attendees_str):
        return []
    return [name.strip() for name in str(attendees_str).split(",") if name.strip()]


def parse_date(date_val: str | datetime) -> datetime | None:
    if not date_val or pd.isna(date_val):
        return None
    if isinstance(date_val, datetime):
        return date_val
    try:
        return datetime.fromisoformat(str(date_val).replace("T", " ").split(".")[0])
    except (ValueError, TypeError):
        return None


def split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.strip().split(maxsplit=1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return full_name.strip(), ""


async def fetch_user_mapping(dest: asyncpg.Connection | None) -> dict[str, uuid.UUID]:
    if dest is None:
        return {}

    logger.info("Fetching user mapping from database...")
    users = await dest.fetch("""
        SELECT id, username, first_name, last_name,
               CONCAT(first_name, ' ', last_name) as full_name
        FROM pyuser.users
    """)

    mapping: dict[str, uuid.UUID] = {}
    for user in users:
        if user["username"]:
            mapping[user["username"].lower()] = user["id"]
        if user["full_name"]:
            mapping[user["full_name"].lower()] = user["id"]
        if user["first_name"] and user["last_name"]:
            mapping[f"{user['first_name']} {user['last_name']}".lower()] = user["id"]

    logger.info(f"Loaded {len(mapping)} user name mappings")
    return mapping


def get_user_id(
    user_name: str,
    user_mapping: dict[str, uuid.UUID],
    default_id: uuid.UUID,
) -> uuid.UUID:
    if not user_name:
        return default_id
    return user_mapping.get(user_name.lower().strip(), default_id)


def parse_sales_team(sales_team: str) -> str | None:
    if not sales_team or pd.isna(sales_team):
        return None
    sales_team = str(sales_team).strip()
    if sales_team.lower() == "house account":
        return None
    parts = [p.strip() for p in sales_team.split(";") if p.strip()]
    if not parts:
        return None
    first_user = parts[0]
    if first_user.lower() == "house account":
        return parts[1] if len(parts) > 1 else None
    return first_user


def get_assigned_to_id(
    sales_team: str,
    user_mapping: dict[str, uuid.UUID],
) -> uuid.UUID | None:
    user_name = parse_sales_team(sales_team)
    if not user_name:
        return None
    return user_mapping.get(user_name.lower().strip())


async def migrate_activity_journals(
    dest: asyncpg.Connection | None,
    df: pd.DataFrame,
    created_by_id: uuid.UUID,
    dry_run: bool = False,
) -> dict[str, int]:
    logger.info("Starting activity journal migration...")

    user_mapping = await fetch_user_mapping(dest)

    task_records = []
    note_records = []
    contact_records = []
    link_records = []
    contact_name_to_id: dict[str, uuid.UUID] = {}
    activity_types: set[str] = set()
    unmapped_users: set[str] = set()

    for _, row in df.iterrows():
        user_name = str(row.get("User Name", "")).strip()
        record_created_by = get_user_id(user_name, user_mapping, created_by_id)
        sales_team = str(row.get("Sales Team", "")).strip()
        assigned_to = get_assigned_to_id(sales_team, user_mapping)

        if user_name and user_name.lower() not in user_mapping:
            unmapped_users.add(user_name)
        task_id = uuid.uuid4()
        activity_type = str(row.get("Type", "")).strip()
        if activity_type:
            activity_types.add(activity_type)

        activity_date = parse_date(row.get("Date"))
        creation_date = parse_date(row.get("Creation Date"))
        created_at = creation_date or activity_date or datetime.now()

        description_parts = []
        comment = str(row.get("Comment", "")).strip()
        if comment:
            description_parts.append(comment)

        company_name = str(row.get("Company Name", "")).strip()
        manufacturer_name = str(row.get("Manufacturer", "")).strip()
        if company_name or manufacturer_name:
            meta_parts = []
            if company_name:
                meta_parts.append(f"Company: {company_name}")
            if manufacturer_name:
                meta_parts.append(f"Manufacturer: {manufacturer_name}")
            description_parts.append("\n\n---\n" + " | ".join(meta_parts))

        task_records.append((
            task_id,
            str(row.get("Subject", "Activity"))[:255],
            TASK_STATUS_COMPLETED,
            TASK_PRIORITY_NORMAL,
            "\n".join(description_parts) if description_parts else None,
            assigned_to,
            activity_date.date() if activity_date else None,
            None,
            [activity_type] if activity_type else None,
            record_created_by,
            created_at,
        ))

        general_rep_notes = str(row.get("General Rep Notes", "")).strip()
        note_id = None
        if general_rep_notes:
            note_id = uuid.uuid4()
            note_records.append((
                note_id,
                f"Rep Notes - {row.get('Subject', 'Activity')}"[:255],
                general_rep_notes,
                None,
                None,
                record_created_by,
                created_at,
            ))
            link_records.append((
                uuid.uuid4(),
                ENTITY_TYPE_TASK,
                task_id,
                ENTITY_TYPE_NOTE,
                note_id,
                record_created_by,
                created_at,
            ))

        attendees = parse_attendees(row.get("Attendees", ""))
        for attendee_name in attendees:
            if attendee_name not in contact_name_to_id:
                contact_id = uuid.uuid4()
                contact_name_to_id[attendee_name] = contact_id
                first_name, last_name = split_name(attendee_name)
                contact_records.append((
                    contact_id,
                    first_name[:100],
                    last_name[:100] if last_name else "",
                    None,
                    None,
                    None,
                    None,
                    None,
                    None,
                    record_created_by,
                    created_at,
                ))

            contact_id = contact_name_to_id[attendee_name]
            link_records.append((
                uuid.uuid4(),
                ENTITY_TYPE_TASK,
                task_id,
                ENTITY_TYPE_CONTACT,
                contact_id,
                record_created_by,
                created_at,
            ))


    logger.info(f"Activity Types found ({len(activity_types)}): {sorted(activity_types)[:10]}...")
    if unmapped_users:
        logger.warning(f"Unmapped users ({len(unmapped_users)}): {sorted(unmapped_users)[:10]}...")

    if dry_run:
        logger.info(f"[DRY RUN] Would insert:")
        logger.info(f"  - {len(task_records)} tasks")
        logger.info(f"  - {len(note_records)} notes")
        logger.info(f"  - {len(contact_records)} contacts")
        logger.info(f"  - {len(link_records)} link relations")
        return {
            "tasks": len(task_records),
            "notes": len(note_records),
            "contacts": len(contact_records),
            "link_relations": len(link_records),
        }

    if contact_records:
        await dest.executemany(
            """
            INSERT INTO pycrm.contacts (
                id, first_name, last_name, email, phone, role, territory,
                tags, notes, created_by_id, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (id) DO NOTHING
            """,
            contact_records,
        )
        logger.info(f"Inserted {len(contact_records)} contacts")

    if task_records:
        await dest.executemany(
            """
            INSERT INTO pycrm.tasks (
                id, title, status, priority, description, assigned_to_id,
                due_date, reminder_date, tags, created_by_id, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (id) DO NOTHING
            """,
            task_records,
        )
        logger.info(f"Inserted {len(task_records)} tasks")

    if note_records:
        await dest.executemany(
            """
            INSERT INTO pycrm.notes (
                id, title, content, tags, mentions, created_by_id, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO NOTHING
            """,
            note_records,
        )
        logger.info(f"Inserted {len(note_records)} notes")

    if link_records:
        await dest.executemany(
            """
            INSERT INTO pycrm.link_relations (
                id, source_entity_type, source_entity_id,
                target_entity_type, target_entity_id,
                created_by_id, created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO NOTHING
            """,
            link_records,
        )
        logger.info(f"Inserted {len(link_records)} link relations")

    return {
        "tasks": len(task_records),
        "notes": len(note_records),
        "contacts": len(contact_records),
        "link_relations": len(link_records),
    }


async def run_migration(config: MigrationConfig) -> dict[str, int]:
    logger.info("Starting Activity Journals migration...")

    df = load_excel_data(config.excel_path)

    if config.dry_run:
        logger.info("[DRY RUN] No database changes will be made")
        return await migrate_activity_journals(None, df, config.created_by_id, dry_run=True)  # type: ignore[arg-type]

    dest = await asyncpg.connect(
        config.dest_dsn,
        timeout=60,
        command_timeout=600.0,
        server_settings={
            "statement_timeout": "0",
            "idle_in_transaction_session_timeout": "0",
        },
    )

    try:
        results = await migrate_activity_journals(dest, df, config.created_by_id, config.dry_run)
        logger.info("Migration completed successfully!")
        logger.info(f"Results: {results}")
        return results
    except Exception as e:
        logger.exception(f"Migration failed: {e}")
        raise
    finally:
        await dest.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate Activity Journals from Excel to Flow v6")
    parser.add_argument("--excel-path", required=True, help="Path to the Excel file")
    parser.add_argument("--dest-url", required=True, help="Destination database URL")
    parser.add_argument("--created-by-id", required=True, help="UUID of the user to set as created_by")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be migrated")
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
