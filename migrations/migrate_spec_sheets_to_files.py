import asyncio
import logging
import os
from uuid import uuid4

import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FileType enum value for PDF
FILE_TYPE_PDF = 3

# EntityType enum values
ENTITY_TYPE_FILE = 14
ENTITY_TYPE_FACTORY = 11


async def migrate_spec_sheets_to_files(conn: asyncpg.Connection) -> int:
    """
    Create File records and LinkRelations for existing spec sheets.

    Returns:
        Number of spec sheets migrated
    """
    logger.info("Starting spec sheets to files migration...")

    # Get all spec sheets without file_id
    spec_sheets = await conn.fetch("""
        SELECT
            ss.id,
            ss.factory_id,
            ss.file_name,
            ss.file_url,
            ss.file_size,
            ss.created_at,
            ss.created_by_id
        FROM pycrm.spec_sheets ss
        WHERE ss.file_id IS NULL
    """)

    if not spec_sheets:
        logger.info("No spec sheets to migrate")
        return 0

    logger.info(f"Found {len(spec_sheets)} spec sheets to migrate")

    migrated_count = 0

    for ss in spec_sheets:
        try:
            # Extract S3 key from file_url if possible, otherwise use a placeholder
            # file_url is usually a presigned URL, we need the S3 key
            file_path = f"spec-sheets/{ss['id']}.pdf"  # Use spec sheet ID as path

            # Create File record
            file_id = uuid4()
            await conn.execute(
                """
                INSERT INTO pyfiles.files (
                    id, file_name, file_path, file_size, file_type,
                    archived, created_at, created_by_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                file_id,
                ss["file_name"],
                file_path,
                ss["file_size"] or 0,
                FILE_TYPE_PDF,
                False,
                ss["created_at"],
                ss["created_by_id"],
            )

            # Create LinkRelation (FILE -> FACTORY)
            link_id = uuid4()
            await conn.execute(
                """
                INSERT INTO pycrm.link_relations (
                    id, source_entity_type, source_entity_id,
                    target_entity_type, target_entity_id,
                    created_at, created_by_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT DO NOTHING
            """,
                link_id,
                ENTITY_TYPE_FILE,
                file_id,
                ENTITY_TYPE_FACTORY,
                ss["factory_id"],
                ss["created_at"],
                ss["created_by_id"],
            )

            # Update spec_sheet with file_id
            await conn.execute(
                """
                UPDATE pycrm.spec_sheets
                SET file_id = $1
                WHERE id = $2
            """,
                file_id,
                ss["id"],
            )

            migrated_count += 1

            if migrated_count % 100 == 0:
                logger.info(f"Migrated {migrated_count}/{len(spec_sheets)} spec sheets")

        except Exception as e:
            logger.error(f"Failed to migrate spec sheet {ss['id']}: {e}")
            continue

    logger.info(f"Migration complete. Migrated {migrated_count} spec sheets")
    return migrated_count


async def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")

    conn = await asyncpg.connect(database_url)
    try:
        async with conn.transaction():
            count = await migrate_spec_sheets_to_files(conn)
            logger.info(f"Total spec sheets migrated: {count}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
