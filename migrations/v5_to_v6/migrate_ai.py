import logging

import asyncpg

logger = logging.getLogger(__name__)

AI_TABLES = [
    "document_clusters",
    "cluster_contexts",
    "pending_documents",
    "pending_document_pages",
    "pending_document_entities",
    "pending_document_correction_changes",
    "extracted_data_versions",
    "pending_entities",
    "entity_match_candidates"
]


async def migrate_ai_table(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
    table_name: str,
) -> int:
    logger.info(f"Starting {table_name} migration...")

    rows = await source.fetch(f"SELECT * FROM ai.{table_name}")  # noqa: S608

    if not rows:
        logger.info(f"No {table_name} to migrate")
        return 0

    columns = list(rows[0].keys())
    placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))
    columns_str = ", ".join(columns)
    update_cols = [c for c in columns if c != "id"]
    update_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    await dest.executemany(
        f"""
        INSERT INTO ai.{table_name} ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT (id) DO UPDATE SET {update_clause}
        """,  # noqa: S608
        [tuple(row[c] for c in columns) for row in rows],
    )

    logger.info(f"Migrated {len(rows)} {table_name}")
    return len(rows)
