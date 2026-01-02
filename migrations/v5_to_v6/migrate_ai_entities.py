import logging

import asyncpg

logger = logging.getLogger(__name__)


async def migrate_extracted_data_versions(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting extracted data version migration...")

    versions = await source.fetch("""
        SELECT
            id,
            pending_document_id,
            version_number,
            data,
            change_description,
            change_type,
            user_instruction,
            executed_code,
            created_by,
            meta_data,
            COALESCE(created_at, now()) as created_at
        FROM i.extracted_data_versions
    """)

    if not versions:
        logger.info("No extracted data versions to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO ai.extracted_data_versions (
            id, pending_document_id, version_number, data, change_description,
            change_type, user_instruction, executed_code, created_by,
            meta_data, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        ON CONFLICT (id) DO UPDATE SET
            pending_document_id = EXCLUDED.pending_document_id,
            version_number = EXCLUDED.version_number,
            data = EXCLUDED.data,
            change_description = EXCLUDED.change_description,
            change_type = EXCLUDED.change_type,
            user_instruction = EXCLUDED.user_instruction,
            executed_code = EXCLUDED.executed_code,
            created_by = EXCLUDED.created_by,
            meta_data = EXCLUDED.meta_data
        """,
        [(
            v["id"],
            v["pending_document_id"],
            v["version_number"],
            v["data"],
            v["change_description"],
            v["change_type"],
            v["user_instruction"],
            v["executed_code"],
            v["created_by"],
            v["meta_data"],
            v["created_at"],
        ) for v in versions],
    )

    logger.info(f"Migrated {len(versions)} extracted data versions")
    return len(versions)


async def migrate_pending_entities(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting pending entity migration...")

    entities = await source.fetch("""
        SELECT
            id,
            entity_type,
            confirmation_status,
            pending_document_id,
            dto_ids,
            flow_index_detail,
            extracted_data,
            display_name,
            source_line_numbers,
            best_match_id,
            best_match_name,
            best_match_similarity,
            confirmed_at,
            confirmed_by_user_id,
            updated_at,
            COALESCE(created_at, now()) as created_at
        FROM i.pending_entities
    """)

    if not entities:
        logger.info("No pending entities to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO ai.pending_entities (
            id, entity_type, confirmation_status, pending_document_id, dto_ids,
            flow_index_detail, extracted_data, display_name, source_line_numbers,
            best_match_id, best_match_name, best_match_similarity, confirmed_at,
            confirmed_by_user_id, updated_at, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
        ON CONFLICT (id) DO UPDATE SET
            entity_type = EXCLUDED.entity_type,
            confirmation_status = EXCLUDED.confirmation_status,
            pending_document_id = EXCLUDED.pending_document_id,
            dto_ids = EXCLUDED.dto_ids,
            flow_index_detail = EXCLUDED.flow_index_detail,
            extracted_data = EXCLUDED.extracted_data,
            display_name = EXCLUDED.display_name,
            source_line_numbers = EXCLUDED.source_line_numbers,
            best_match_id = EXCLUDED.best_match_id,
            best_match_name = EXCLUDED.best_match_name,
            best_match_similarity = EXCLUDED.best_match_similarity,
            confirmed_at = EXCLUDED.confirmed_at,
            confirmed_by_user_id = EXCLUDED.confirmed_by_user_id,
            updated_at = EXCLUDED.updated_at
        """,
        [(
            e["id"],
            e["entity_type"],
            e["confirmation_status"],
            e["pending_document_id"],
            e["dto_ids"],
            e["flow_index_detail"],
            e["extracted_data"],
            e["display_name"],
            e["source_line_numbers"],
            e["best_match_id"],
            e["best_match_name"],
            e["best_match_similarity"],
            e["confirmed_at"],
            e["confirmed_by_user_id"],
            e["updated_at"],
            e["created_at"],
        ) for e in entities],
    )

    logger.info(f"Migrated {len(entities)} pending entities")
    return len(entities)


async def migrate_entity_match_candidates(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting entity match candidate migration...")

    candidates = await source.fetch("""
        SELECT
            id,
            pending_entity_id,
            existing_entity_id,
            existing_entity_name,
            similarity_score,
            rank,
            match_metadata
        FROM i.entity_match_candidates
    """)

    if not candidates:
        logger.info("No entity match candidates to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO ai.entity_match_candidates (
            id, pending_entity_id, existing_entity_id, existing_entity_name,
            similarity_score, rank, match_metadata
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO UPDATE SET
            pending_entity_id = EXCLUDED.pending_entity_id,
            existing_entity_id = EXCLUDED.existing_entity_id,
            existing_entity_name = EXCLUDED.existing_entity_name,
            similarity_score = EXCLUDED.similarity_score,
            rank = EXCLUDED.rank,
            match_metadata = EXCLUDED.match_metadata
        """,
        [(
            c["id"],
            c["pending_entity_id"],
            c["existing_entity_id"],
            c["existing_entity_name"],
            c["similarity_score"],
            c["rank"],
            c["match_metadata"],
        ) for c in candidates],
    )

    logger.info(f"Migrated {len(candidates)} entity match candidates")
    return len(candidates)
