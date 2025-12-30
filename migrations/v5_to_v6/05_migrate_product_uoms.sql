-- Migration: Product UOMs from v5 (core.product_uoms) to v6 (pycore.product_uoms)
-- Run order: 05
-- Dependencies: 01_migrate_users.sql

-- v5 schema: core.product_uoms (id, title, description, entry_date, created_by, creation_type, ...)
-- v6 schema: pycore.product_uoms (title, creation_type, description, id, created_by_id, created_at, division_factor)

INSERT INTO pycore.product_uoms (
    id,
    title,
    description,
    creation_type,
    created_by_id,
    created_at,
    division_factor
)
SELECT
    u.id,
    u.title,
    u.description,
    u.creation_type,
    u.created_by,
    COALESCE(u.entry_date, now()),
    CASE
        WHEN u.multiply AND u.multiply_by > 0 THEN u.multiply_by::numeric(18,6)
        ELSE NULL
    END AS division_factor  -- Map multiply_by to division_factor
FROM core.product_uoms u
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    creation_type = EXCLUDED.creation_type,
    division_factor = EXCLUDED.division_factor;
