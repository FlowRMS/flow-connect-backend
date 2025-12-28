-- Migration: Files and Folders from v5 (files.*) to v6 (pyfiles.*)
-- Run order: 03
-- Dependencies: 01_migrate_users.sql (requires users for created_by_id)

-- Migrate folders first (files depend on folders)
-- v5 schema: files.folders (id, name, create_date, created_by, updated_by, update_date, count_of_files, archived, s3_path, is_public)
-- v6 schema: pyfiles.folders (name, description, parent_id, archived, id, created_at, created_by_id)

INSERT INTO pyfiles.folders (
    id,
    name,
    description,
    parent_id,
    archived,
    created_at,
    created_by_id
)
SELECT
    f.id,
    f.name,
    NULL,  -- No description in v5
    NULL,  -- No parent_id in v5 folders structure
    f.archived,
    COALESCE(f.create_date, now()),
    f.created_by
FROM files.folders f
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    archived = EXCLUDED.archived;

-- Migrate files
-- v5 schema: files.files (file_name, file_path, created_by, created_at, file_type, id, archived, ...)
-- v6 schema: pyfiles.files (file_name, file_path, file_size, file_type, file_sha, archived, folder_id, id, created_at, created_by_id)

INSERT INTO pyfiles.files (
    id,
    file_name,
    file_path,
    file_size,
    file_type,
    file_sha,
    archived,
    folder_id,
    created_at,
    created_by_id
)
SELECT
    f.id,
    f.file_name,
    f.file_path,
    COALESCE(f.file_size, 0),
    -- Map file_type string to smallint enum
    CASE
        WHEN UPPER(f.file_type) IN ('PDF') THEN 1
        WHEN UPPER(f.file_type) IN ('CSV') THEN 2
        WHEN UPPER(f.file_type) IN ('XLS', 'XLSX') THEN 3
        WHEN UPPER(f.file_type) IN ('DOC', 'DOCX') THEN 4
        WHEN UPPER(f.file_type) IN ('JPG', 'JPEG', 'PNG', 'GIF') THEN 5
        ELSE NULL
    END AS file_type,
    f.file_sha,
    COALESCE(f.archived, false),
    f.folder_id,
    COALESCE(f.created_at, now()),
    f.created_by
FROM files.files f
ON CONFLICT (id) DO UPDATE SET
    file_name = EXCLUDED.file_name,
    file_path = EXCLUDED.file_path,
    file_size = EXCLUDED.file_size,
    file_type = EXCLUDED.file_type,
    archived = EXCLUDED.archived,
    folder_id = EXCLUDED.folder_id;
