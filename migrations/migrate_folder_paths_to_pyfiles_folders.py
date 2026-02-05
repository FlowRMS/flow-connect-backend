import asyncio
import logging
import os
from uuid import UUID, uuid4

import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_folder_paths_to_pyfiles(conn: asyncpg.Connection) -> dict[str, int]:
    """
    Convert folder_path strings to pyfiles.folders hierarchy.

    Returns:
        Dict with counts: folders_created, mappings_created, files_updated
    """
    logger.info("Starting folder_path to pyfiles.folders migration...")

    # Get all unique (factory_id, folder_path) combinations
    rows = await conn.fetch("""
        SELECT DISTINCT ss.factory_id, ss.folder_path
        FROM pycrm.spec_sheets ss
        WHERE ss.folder_path IS NOT NULL AND ss.folder_path != ''
        UNION
        SELECT factory_id, folder_path
        FROM pycrm.spec_sheet_folders
        WHERE folder_path IS NOT NULL AND folder_path != ''
    """)

    if not rows:
        logger.info("No folder paths to migrate")
        return {"folders_created": 0, "mappings_created": 0, "files_updated": 0}

    # Group by factory
    factory_paths: dict[UUID, set[str]] = {}
    for row in rows:
        factory_id = row["factory_id"]
        folder_path = row["folder_path"]
        if factory_id not in factory_paths:
            factory_paths[factory_id] = set()
        factory_paths[factory_id].add(folder_path)

    logger.info(f"Found {len(factory_paths)} factories with folders to migrate")

    folders_created = 0
    mappings_created = 0
    files_updated = 0

    # Get a system user for created_by_id (first admin user)
    system_user = await conn.fetchrow("""
        SELECT id FROM pyuser.users LIMIT 1
    """)
    system_user_id = system_user["id"] if system_user else None

    for factory_id, paths in factory_paths.items():
        logger.info(f"Processing factory {factory_id} with {len(paths)} folder paths")

        # Extract all unique path segments
        # "A/B/C" needs folders: A, A/B, A/B/C
        all_paths: set[str] = set()
        for path in paths:
            parts = path.split("/")
            for i in range(1, len(parts) + 1):
                all_paths.add("/".join(parts[:i]))

        # Sort by depth (shortest first for proper parent creation)
        sorted_paths = sorted(all_paths, key=lambda p: p.count("/"))

        # Map: path -> folder_id
        path_to_folder_id: dict[str, UUID] = {}

        for path in sorted_paths:
            parts = path.split("/")
            name = parts[-1]
            parent_path = "/".join(parts[:-1]) if len(parts) > 1 else None
            parent_id = path_to_folder_id.get(parent_path) if parent_path else None

            # Create pyfiles.folders record
            folder_id = uuid4()
            await conn.execute(
                """
                INSERT INTO pyfiles.folders (id, name, parent_id, archived, created_at, created_by_id)
                VALUES ($1, $2, $3, false, NOW(), $4)
                """,
                folder_id,
                name,
                parent_id,
                system_user_id,
            )
            folders_created += 1

            path_to_folder_id[path] = folder_id

            # Create spec_sheet_folders mapping
            mapping_id = uuid4()
            await conn.execute(
                """
                INSERT INTO pycrm.spec_sheet_folders (id, factory_id, folder_path, pyfiles_folder_id, created_at)
                VALUES ($1, $2, $3, $4, NOW())
                ON CONFLICT (factory_id, folder_path)
                DO UPDATE SET pyfiles_folder_id = EXCLUDED.pyfiles_folder_id
                """,
                mapping_id,
                factory_id,
                path,
                folder_id,
            )
            mappings_created += 1

        # Update File.folder_id for all spec sheets in this factory
        for path, folder_id in path_to_folder_id.items():
            result = await conn.execute(
                """
                UPDATE pyfiles.files f
                SET folder_id = $1
                FROM pycrm.spec_sheets ss
                WHERE f.id = ss.file_id
                  AND ss.factory_id = $2
                  AND ss.folder_path = $3
                  AND ss.file_id IS NOT NULL
                """,
                folder_id,
                factory_id,
                path,
            )
            # Parse the result to get count (format: "UPDATE N")
            if result:
                count = int(result.split()[-1])
                files_updated += count

    logger.info(
        f"Migration complete: {folders_created} folders created, "
        f"{mappings_created} mappings created, {files_updated} files updated"
    )

    return {
        "folders_created": folders_created,
        "mappings_created": mappings_created,
        "files_updated": files_updated,
    }


async def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is required")

    conn = await asyncpg.connect(database_url)
    try:
        async with conn.transaction():
            result = await migrate_folder_paths_to_pyfiles(conn)
            logger.info(f"Migration results: {result}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
