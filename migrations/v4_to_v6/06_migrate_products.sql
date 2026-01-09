-- Migration: Products from v4 (public.products) to v6 (pycore.products)
-- Run order: 06
-- Dependencies: 03_migrate_factories.sql, 04_migrate_product_uoms.sql, 05_migrate_product_categories.sql

-- v4 schema: public.products (product_id, alternate_ean, base_price, case_upc, commission_rate, unit_price,
--            description, ean, image_url, ind_upc, list_price, min_order_qty, factory_part_number, status,
--            uom, factory_id, approval_comments, approval_date, approval_needed, uuid, lead_time, price_by,
--            create_date, created_by, creation_type, uom_id, dimensions_id, commission_discount_rate,
--            discount_rate, visibility, category_uuid)
-- v6 schema: pycore.products (factory_part_number, unit_price, default_commission_rate, factory_id,
--            product_category_id, product_uom_id, published, approval_needed, description, creation_type,
--            id, created_at, created_by_id, upc, default_divisor, min_order_qty, lead_time,
--            unit_price_discount_rate, commission_discount_rate, approval_date, approval_comments, tags)

INSERT INTO pycore.products (
    id,
    factory_part_number,
    unit_price,
    default_commission_rate,
    factory_id,
    product_category_id,
    product_uom_id,
    published,
    approval_needed,
    description,
    creation_type,
    created_at,
    created_by_id,
    upc,
    default_divisor,
    min_order_qty,
    lead_time,
    unit_price_discount_rate,
    commission_discount_rate,
    approval_date,
    approval_comments,
    tags
)
SELECT
    p.uuid,
    p.factory_part_number,
    COALESCE(p.unit_price, 0),
    COALESCE(p.commission_rate, 0),
    f.uuid,  -- Map integer factory_id to factory's uuid
    p.category_uuid,  -- category_uuid is already uuid in v4
    p.uom_id,  -- uom_id is already uuid in v4
    COALESCE(p.status, true),  -- Map status to published
    COALESCE(p.approval_needed, false),
    p.description,
    p.creation_type,
    COALESCE(p.create_date, now()),
    p.created_by,
    p.ind_upc,  -- Map ind_upc to upc
    NULL,  -- default_divisor not in v4
    p.min_order_qty,
    CASE
        WHEN p.lead_time ~ '^\d+$' THEN p.lead_time::integer
        ELSE NULL
    END AS lead_time,
    p.discount_rate,  -- Map discount_rate to unit_price_discount_rate
    p.commission_discount_rate,
    p.approval_date,
    p.approval_comments,
    NULL  -- No tags in v4
FROM public.products p
LEFT JOIN public.factories f ON p.factory_id = f.factory_id
ON CONFLICT (id) DO UPDATE SET
    factory_part_number = EXCLUDED.factory_part_number,
    unit_price = EXCLUDED.unit_price,
    default_commission_rate = EXCLUDED.default_commission_rate,
    factory_id = EXCLUDED.factory_id,
    product_category_id = EXCLUDED.product_category_id,
    product_uom_id = EXCLUDED.product_uom_id,
    published = EXCLUDED.published,
    approval_needed = EXCLUDED.approval_needed,
    description = EXCLUDED.description,
    creation_type = EXCLUDED.creation_type,
    upc = EXCLUDED.upc,
    min_order_qty = EXCLUDED.min_order_qty,
    lead_time = EXCLUDED.lead_time,
    unit_price_discount_rate = EXCLUDED.unit_price_discount_rate,
    commission_discount_rate = EXCLUDED.commission_discount_rate,
    approval_date = EXCLUDED.approval_date,
    approval_comments = EXCLUDED.approval_comments;
