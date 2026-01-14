-- Migration: Product Categories from v4 (public.product_categories) to v6 (pycore.product_categories)
-- Run order: 05
-- Dependencies: 03_migrate_factories.sql (categories reference factories)

-- v4 schema: public.product_categories (title, commission_rate, factory_id, uuid)
-- v6 schema: pycore.product_categories (title, commission_rate, factory_id, parent_id, grandparent_id, id)

-- Note: v4 factory_id is integer, need to map via factory uuid
-- Note: v6 has parent_id and grandparent_id for hierarchical categories which v4 doesn't have

INSERT INTO pycore.product_categories (
    id,
    title,
    commission_rate,
    factory_id,
    parent_id,
    grandparent_id
)
SELECT
    pc.uuid,
    pc.title,
    COALESCE(pc.commission_rate, 0),
    f.uuid,  -- Map integer factory_id to factory's uuid
    NULL,  -- No parent_id in v4
    NULL   -- No grandparent_id in v4
FROM public.product_categories pc
JOIN public.factories f ON pc.factory_id = f.factory_id
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    commission_rate = EXCLUDED.commission_rate,
    factory_id = EXCLUDED.factory_id;
