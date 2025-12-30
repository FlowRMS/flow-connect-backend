-- Migration: Product Categories from v5 (core.product_categories) to v6 (pycore.product_categories)
-- Run order: 06
-- Dependencies: 04_migrate_factories.sql (categories reference factories)

-- v5 schema: core.product_categories (id, title, factory_id, commission_rate, entry_date, created_by, creation_type, ...)
-- v6 schema: pycore.product_categories (title, commission_rate, factory_id, parent_id, grandparent_id, id)

-- Note: v6 has parent_id and grandparent_id for hierarchical categories which v5 doesn't have

INSERT INTO pycore.product_categories (
    id,
    title,
    commission_rate,
    factory_id,
    parent_id,
    grandparent_id
)
SELECT
    pc.id,
    pc.title,
    COALESCE(pc.commission_rate, 0),
    pc.factory_id,
    NULL,  -- No parent_id in v5
    NULL   -- No grandparent_id in v5
FROM core.product_categories pc
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    commission_rate = EXCLUDED.commission_rate,
    factory_id = EXCLUDED.factory_id;
