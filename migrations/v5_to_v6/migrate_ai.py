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
    "entity_match_candidates",
]


async def migrate_ai_table(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
    table_name: str,
) -> int:
    logger.info(f"Starting {table_name} migration...")

    rows = await source.fetch(f"SELECT * FROM ai.{table_name}")

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


async def migrate_pending_documents(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting pending_documents migration...")

    rows = await source.fetch("""
        SELECT pd.*
        FROM ai.pending_documents pd
        LEFT JOIN pycore.files f ON f.id = pd.file_id
        WHERE pd.file_id IS NULL OR f.id IS NOT NULL
    """)

    if not rows:
        logger.info("No pending_documents to migrate")
        return 0

    columns = list(rows[0].keys())
    placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))
    columns_str = ", ".join(columns)
    update_cols = [c for c in columns if c != "id"]
    update_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    await dest.executemany(
        f"""
        INSERT INTO ai.pending_documents ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT (id) DO UPDATE SET {update_clause}
        """,
        [tuple(row[c] for c in columns) for row in rows],
    )

    logger.info(f"Migrated {len(rows)} pending_documents")
    return len(rows)


async def migrate_pending_document_pages(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting pending_document_pages migration...")

    rows = await source.fetch("""
        SELECT pdp.*
        FROM ai.pending_document_pages pdp
        JOIN ai.pending_documents pd ON pd.id = pdp.pending_document_id
        LEFT JOIN pycore.files f ON f.id = pd.file_id
        WHERE pd.file_id IS NULL OR f.id IS NOT NULL
    """)

    if not rows:
        logger.info("No pending_document_pages to migrate")
        return 0

    columns = list(rows[0].keys())
    placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))
    columns_str = ", ".join(columns)
    update_cols = [c for c in columns if c != "id"]
    update_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    await dest.executemany(
        f"""
        INSERT INTO ai.pending_document_pages ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT (id) DO UPDATE SET {update_clause}
        """,
        [tuple(row[c] for c in columns) for row in rows],
    )

    logger.info(f"Migrated {len(rows)} pending_document_pages")
    return len(rows)


async def migrate_pending_document_entities(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting pending_document_entities migration...")

    rows = await source.fetch("""
        SELECT pde.*
        FROM ai.pending_document_entities pde
        JOIN ai.pending_documents pd ON pd.id = pde.pending_document_id
        LEFT JOIN pycore.files f ON f.id = pd.file_id
        WHERE pd.file_id IS NULL OR f.id IS NOT NULL
    """)

    if not rows:
        logger.info("No pending_document_entities to migrate")
        return 0

    columns = list(rows[0].keys())
    placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))
    columns_str = ", ".join(columns)
    update_cols = [c for c in columns if c != "id"]
    update_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    await dest.executemany(
        f"""
        INSERT INTO ai.pending_document_entities ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT (id) DO UPDATE SET {update_clause}
        """,
        [tuple(row[c] for c in columns) for row in rows],
    )

    logger.info(f"Migrated {len(rows)} pending_document_entities")
    return len(rows)


async def migrate_pending_document_correction_changes(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting pending_document_correction_changes migration...")

    rows = await source.fetch("""
        SELECT pdcc.*
        FROM ai.pending_document_correction_changes pdcc
        JOIN ai.pending_documents pd ON pd.id = pdcc.pending_document_id
        LEFT JOIN pycore.files f ON f.id = pd.file_id
        WHERE pd.file_id IS NULL OR f.id IS NOT NULL
    """)

    if not rows:
        logger.info("No pending_document_correction_changes to migrate")
        return 0

    columns = list(rows[0].keys())
    placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))
    columns_str = ", ".join(columns)
    update_cols = [c for c in columns if c != "id"]
    update_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    await dest.executemany(
        f"""
        INSERT INTO ai.pending_document_correction_changes ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT (id) DO UPDATE SET {update_clause}
        """,
        [tuple(row[c] for c in columns) for row in rows],
    )

    logger.info(f"Migrated {len(rows)} pending_document_correction_changes")
    return len(rows)


async def migrate_extracted_data_versions(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting extracted_data_versions migration...")

    rows = await source.fetch("""
        SELECT edv.*
        FROM ai.extracted_data_versions edv
        JOIN ai.pending_documents pd ON pd.id = edv.pending_document_id
        LEFT JOIN pycore.files f ON f.id = pd.file_id
        WHERE pd.file_id IS NULL OR f.id IS NOT NULL
    """)

    if not rows:
        logger.info("No extracted_data_versions to migrate")
        return 0

    columns = list(rows[0].keys())
    placeholders = ", ".join(f"${i + 1}" for i in range(len(columns)))
    columns_str = ", ".join(columns)
    update_cols = [c for c in columns if c != "id"]
    update_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    await dest.executemany(
        f"""
        INSERT INTO ai.extracted_data_versions ({columns_str})
        VALUES ({placeholders})
        ON CONFLICT (id) DO UPDATE SET {update_clause}
        """,
        [tuple(row[c] for c in columns) for row in rows],
    )

    logger.info(f"Migrated {len(rows)} extracted_data_versions")
    return len(rows)
