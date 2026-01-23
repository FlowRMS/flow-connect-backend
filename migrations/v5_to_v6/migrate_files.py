import logging

import asyncpg

logger = logging.getLogger(__name__)


async def migrate_folders(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    logger.info("Starting folder migration...")

    folders = await source.fetch("""
        SELECT
            f.id,
            f.name,
            COALESCE(f.archived, false) as archived,
            COALESCE(f.create_date, now()) as created_at,
            f.created_by as created_by_id
        FROM files.folders f
        JOIN "user".users u ON f.created_by = u.id
    """)

    if not folders:
        logger.info("No folders to migrate")
        return 0

    await dest.executemany(
        """
        INSERT INTO pyfiles.folders (
            id, name, description, parent_id, archived, created_at, created_by_id
        ) VALUES ($1, $2, NULL, NULL, $3, $4, $5)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            archived = EXCLUDED.archived
        """,
        [(
            f["id"],
            f["name"],
            f["archived"],
            f["created_at"],
            f["created_by_id"],
        ) for f in folders],
    )

    logger.info(f"Migrated {len(folders)} folders")
    return len(folders)


async def migrate_files(source: asyncpg.Connection, dest: asyncpg.Connection) -> int:
    logger.info("Starting file migration...")

    files = await source.fetch("""
        SELECT
            f.id,
            f.file_name,
            f.file_path,
            COALESCE(f.file_size, 0) as file_size,
            f.file_type,
            f.file_sha,
            COALESCE(f.archived, false) as archived,
            f.folder_id,
            COALESCE(f.created_at, now()) as created_at,
            COALESCE(u.id, (SELECT id FROM "user".users LIMIT 1)) as created_by_id
        FROM files.files f
        LEFT JOIN "user".users u ON f.created_by = u.id
    """)

    if not files:
        logger.info("No files to migrate")
        return 0

    def map_file_type(file_type: str | None) -> int | None:
        if not file_type:
            return None
        file_type_upper = file_type.upper()
        if file_type_upper == "PDF":
            return 1
        if file_type_upper == "CSV":
            return 2
        if file_type_upper in ("XLS", "XLSX"):
            return 3
        if file_type_upper in ("DOC", "DOCX"):
            return 4
        if file_type_upper in ("JPG", "JPEG", "PNG", "GIF"):
            return 5
        return None

    await dest.executemany(
        """
        INSERT INTO pyfiles.files (
            id, file_name, file_path, file_size, file_type, file_sha,
            archived, folder_id, created_at, created_by_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (id) DO UPDATE SET
            file_name = EXCLUDED.file_name,
            file_path = EXCLUDED.file_path,
            file_size = EXCLUDED.file_size,
            file_type = EXCLUDED.file_type,
            archived = EXCLUDED.archived,
            folder_id = EXCLUDED.folder_id
        """,
        [(
            f["id"],
            f["file_name"],
            f["file_path"],
            f["file_size"],
            map_file_type(f["file_type"]),
            f["file_sha"],
            f["archived"],
            f["folder_id"],
            f["created_at"],
            f["created_by_id"],
        ) for f in files],
    )

    logger.info(f"Migrated {len(files)} files")
    return len(files)
