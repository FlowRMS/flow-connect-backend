import logging

import asyncpg

logger = logging.getLogger(__name__)


async def migrate_notes(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate notes from pycrm.notes using SELECT *."""
    logger.info("Starting notes migration...")

    notes = await source.fetch("SELECT * FROM pycrm.notes")

    if not notes:
        logger.info("No notes to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.notes (
            id, title, content, tags, mentions, created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            content = EXCLUDED.content,
            tags = EXCLUDED.tags,
            mentions = EXCLUDED.mentions
        """,
        [(
            n["id"],
            n["title"],
            n["content"],
            n["tags"],
            n["mentions"],
            n["created_by_id"],
            n["created_at"],
        ) for n in notes],
    )

    logger.info(f"Migrated {len(notes)} notes")
    return len(notes)


async def migrate_tasks(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate tasks from pycrm.tasks using SELECT *."""
    logger.info("Starting tasks migration...")

    tasks = await source.fetch("SELECT * FROM pycrm.tasks")

    if not tasks:
        logger.info("No tasks to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.tasks (
            id, title, status, priority, description, assigned_to_id,
            due_date, reminder_date, tags, created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            status = EXCLUDED.status,
            priority = EXCLUDED.priority,
            description = EXCLUDED.description,
            assigned_to_id = EXCLUDED.assigned_to_id,
            due_date = EXCLUDED.due_date,
            reminder_date = EXCLUDED.reminder_date,
            tags = EXCLUDED.tags
        """,
        [(
            t["id"],
            t["title"],
            t["status"],
            t["priority"],
            t["description"],
            t["assigned_to_id"],
            t["due_date"],
            t["reminder_date"],
            t["tags"],
            t["created_by_id"],
            t["created_at"],
        ) for t in tasks],
    )

    logger.info(f"Migrated {len(tasks)} tasks")
    return len(tasks)


async def migrate_link_relations(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate link relations from pycrm.link_relations using SELECT *."""
    logger.info("Starting link relations migration...")

    links = await source.fetch("""SELECT l.* FROM pycrm.link_relations l JOIN "user".users ON l.created_by_id = users.id""")

    if not links:
        logger.info("No link relations to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.link_relations (
            id, source_entity_type, source_entity_id,
            target_entity_type, target_entity_id,
            created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO UPDATE SET
            source_entity_type = EXCLUDED.source_entity_type,
            source_entity_id = EXCLUDED.source_entity_id,
            target_entity_type = EXCLUDED.target_entity_type,
            target_entity_id = EXCLUDED.target_entity_id
        """,
        [(
            link["id"],
            link["source_entity_type"],
            link["source_entity_id"],
            link["target_entity_type"],
            link["target_entity_id"],
            link["created_by_id"],
            link["created_at"],
        ) for link in links],
    )

    logger.info(f"Migrated {len(links)} link relations")
    return len(links)


async def migrate_companies(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    """Migrate companies from pycrm.companies using SELECT *."""
    logger.info("Starting companies migration...")

    companies = await source.fetch("SELECT * FROM pycrm.companies")

    if not companies:
        logger.info("No companies to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pycrm.companies (
            id, name, company_source_type, website, phone, tags,
            parent_company_id, created_by_id, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            company_source_type = EXCLUDED.company_source_type,
            website = EXCLUDED.website,
            phone = EXCLUDED.phone,
            tags = EXCLUDED.tags,
            parent_company_id = EXCLUDED.parent_company_id
        """,
        [(
            c["id"],
            c["name"],
            c["company_source_type"],
            c["website"],
            c["phone"],
            c["tags"],
            c["parent_company_id"],
            c["created_by_id"],
            c["created_at"],
        ) for c in companies],
    )

    logger.info(f"Migrated {len(companies)} companies")
    return len(companies)
