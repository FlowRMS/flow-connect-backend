-- Migration: Product UOMs from v4 (public.unit_of_measures) to v6 (pycore.product_uoms)
-- Run order: 04
-- Dependencies: 01_migrate_users.sql

-- v4 schema: public.unit_of_measures (title, uom_id, multiply, multiply_by, description)
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
    u.uom_id,
    u.title,
    u.description,
    'migration',  -- Default creation_type
    NULL,  -- No created_by in v4
    now(),
    CASE
        WHEN u.multiply AND u.multiply_by > 0 THEN u.multiply_by::numeric(18,6)
        ELSE NULL
    END AS division_factor
FROM public.unit_of_measures u
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    description = EXCLUDED.description,
    division_factor = EXCLUDED.division_factor;
