import logging

import asyncpg

logger = logging.getLogger(__name__)


async def migrate_document_clusters(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting document cluster migration...")

    clusters = await source.fetch("""
        SELECT
            id,
            cluster_name,
            cluster_metadata,
            COALESCE(is_hidden, false) as is_hidden,
            COALESCE(created_at, now()) as created_at
        FROM i.document_clusters
    """)

    if not clusters:
        logger.info("No document clusters to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO ai.document_clusters (
            id, cluster_name, cluster_metadata, is_hidden, created_at
        ) VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (id) DO UPDATE SET
            cluster_name = EXCLUDED.cluster_name,
            cluster_metadata = EXCLUDED.cluster_metadata,
            is_hidden = EXCLUDED.is_hidden
        """,
        [(
            c["id"],
            c["cluster_name"],
            c["cluster_metadata"],
            c["is_hidden"],
            c["created_at"],
        ) for c in clusters],
    )

    logger.info(f"Migrated {len(clusters)} document clusters")
    return len(clusters)


async def migrate_cluster_contexts(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting cluster context migration...")

    contexts = await source.fetch("""
        SELECT
            id,
            cluster_id,
            file_id,
            file_name,
            converted_text_content,
            file_type,
            COALESCE(created_at, now()) as created_at
        FROM i.cluster_contexts
    """)

    if not contexts:
        logger.info("No cluster contexts to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO ai.cluster_contexts (
            id, cluster_id, file_id, file_name, converted_text_content,
            file_type, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO UPDATE SET
            cluster_id = EXCLUDED.cluster_id,
            file_id = EXCLUDED.file_id,
            file_name = EXCLUDED.file_name,
            converted_text_content = EXCLUDED.converted_text_content,
            file_type = EXCLUDED.file_type
        """,
        [(
            c["id"],
            c["cluster_id"],
            c["file_id"],
            c["file_name"],
            c["converted_text_content"],
            c["file_type"],
            c["created_at"],
        ) for c in contexts],
    )

    logger.info(f"Migrated {len(contexts)} cluster contexts")
    return len(contexts)


async def migrate_pending_documents(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting pending document migration...")

    docs = await source.fetch("""
        SELECT
            id,
            file_id,
            cluster_id,
            original_presigned_url,
            document_type,
            document_sample_content,
            entity_type,
            source_type,
            source_name,
            similar_documents_json,
            extracted_data_json,
            converted_document_url,
            file_upload_process_id,
            COALESCE(additional_instructions_json, '[]'::jsonb) as additional_instructions_json,
            source_classification_json,
            status,
            updated_at,
            sha,
            COALESCE(is_archived, false) as is_archived,
            COALESCE(created_at, now()) as created_at
        FROM i.pending_documents
    """)

    if not docs:
        logger.info("No pending documents to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO ai.pending_documents (
            id, file_id, cluster_id, original_presigned_url, document_type,
            document_sample_content, entity_type, source_type, source_name,
            similar_documents_json, extracted_data_json, converted_document_url,
            file_upload_process_id, additional_instructions_json,
            source_classification_json, status, updated_at, sha, is_archived, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
        ON CONFLICT (id) DO UPDATE SET
            file_id = EXCLUDED.file_id,
            cluster_id = EXCLUDED.cluster_id,
            original_presigned_url = EXCLUDED.original_presigned_url,
            document_type = EXCLUDED.document_type,
            document_sample_content = EXCLUDED.document_sample_content,
            entity_type = EXCLUDED.entity_type,
            source_type = EXCLUDED.source_type,
            source_name = EXCLUDED.source_name,
            similar_documents_json = EXCLUDED.similar_documents_json,
            extracted_data_json = EXCLUDED.extracted_data_json,
            converted_document_url = EXCLUDED.converted_document_url,
            additional_instructions_json = EXCLUDED.additional_instructions_json,
            source_classification_json = EXCLUDED.source_classification_json,
            status = EXCLUDED.status,
            updated_at = EXCLUDED.updated_at,
            sha = EXCLUDED.sha,
            is_archived = EXCLUDED.is_archived
        """,
        [(
            d["id"],
            d["file_id"],
            d["cluster_id"],
            d["original_presigned_url"],
            d["document_type"],
            d["document_sample_content"],
            d["entity_type"],
            d["source_type"],
            d["source_name"],
            d["similar_documents_json"],
            d["extracted_data_json"],
            d["converted_document_url"],
            d["file_upload_process_id"],
            d["additional_instructions_json"],
            d["source_classification_json"],
            d["status"],
            d["updated_at"],
            d["sha"],
            d["is_archived"],
            d["created_at"],
        ) for d in docs],
    )

    logger.info(f"Migrated {len(docs)} pending documents")
    return len(docs)


async def migrate_pending_document_pages(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting pending document page migration...")

    pages = await source.fetch("""
        SELECT
            id,
            pending_document_id,
            page_number,
            markdown_content,
            entity_number,
            page_type,
            COALESCE(is_relevant_for_transactions, false) as is_relevant_for_transactions,
            reasoning,
            number_of_detail_lines,
            COALESCE(created_at, now()) as created_at
        FROM i.pending_document_pages
    """)

    if not pages:
        logger.info("No pending document pages to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO ai.pending_document_pages (
            id, pending_document_id, page_number, markdown_content, entity_number,
            page_type, is_relevant_for_transactions, reasoning,
            number_of_detail_lines, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (id) DO UPDATE SET
            pending_document_id = EXCLUDED.pending_document_id,
            page_number = EXCLUDED.page_number,
            markdown_content = EXCLUDED.markdown_content,
            entity_number = EXCLUDED.entity_number,
            page_type = EXCLUDED.page_type,
            is_relevant_for_transactions = EXCLUDED.is_relevant_for_transactions,
            reasoning = EXCLUDED.reasoning,
            number_of_detail_lines = EXCLUDED.number_of_detail_lines
        """,
        [(
            p["id"],
            p["pending_document_id"],
            p["page_number"],
            p["markdown_content"],
            p["entity_number"],
            p["page_type"],
            p["is_relevant_for_transactions"],
            p["reasoning"],
            p["number_of_detail_lines"],
            p["created_at"],
        ) for p in pages],
    )

    logger.info(f"Migrated {len(pages)} pending document pages")
    return len(pages)


async def migrate_pending_document_entities(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting pending document entity migration...")

    entities = await source.fetch("""
        SELECT
            id,
            pending_document_id,
            entity_id,
            entity_type,
            action,
            COALESCE(created_at, now()) as created_at
        FROM i.pending_document_entities
    """)

    if not entities:
        logger.info("No pending document entities to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO ai.pending_document_entities (
            id, pending_document_id, entity_id, entity_type, action, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
            pending_document_id = EXCLUDED.pending_document_id,
            entity_id = EXCLUDED.entity_id,
            entity_type = EXCLUDED.entity_type,
            action = EXCLUDED.action
        """,
        [(
            e["id"],
            e["pending_document_id"],
            e["entity_id"],
            e["entity_type"],
            e["action"],
            e["created_at"],
        ) for e in entities],
    )

    logger.info(f"Migrated {len(entities)} pending document entities")
    return len(entities)


async def migrate_pending_document_correction_changes(
    source: asyncpg.Connection,
    dest: asyncpg.Connection,
) -> int:
    logger.info("Starting pending document correction change migration...")

    changes = await source.fetch("""
        SELECT
            id,
            pending_document_id,
            correction_action,
            old_value,
            new_value,
            COALESCE(created_at, now()) as created_at
        FROM i.pending_document_correction_changes
    """)

    if not changes:
        logger.info("No pending document correction changes to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO ai.pending_document_correction_changes (
            id, pending_document_id, correction_action, old_value, new_value, created_at
        ) VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (id) DO UPDATE SET
            pending_document_id = EXCLUDED.pending_document_id,
            correction_action = EXCLUDED.correction_action,
            old_value = EXCLUDED.old_value,
            new_value = EXCLUDED.new_value
        """,
        [(
            c["id"],
            c["pending_document_id"],
            c["correction_action"],
            c["old_value"],
            c["new_value"],
            c["created_at"],
        ) for c in changes],
    )

    logger.info(f"Migrated {len(changes)} pending document correction changes")
    return len(changes)
