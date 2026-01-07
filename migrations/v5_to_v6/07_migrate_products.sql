-- Migration: Products from v5 (core.products) to v6 (pycore.products)
-- Run order: 07
-- Dependencies: 04_migrate_factories.sql, 05_migrate_product_uoms.sql, 06_migrate_product_categories.sql

-- v5 schema: core.products (id, entry_date, created_by, creation_type, factory_part_number, factory_id,
--            product_category_id, product_uom_id, lead_time, description, unit_price, min_order_qty,
--            default_commission_rate, commission_discount_rate, overall_discount_rate, cost,
--            individual_upc, published, approval_needed, approval_date, approval_comments, ...)
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
    p.id,
    p.factory_part_number,
    COALESCE(p.unit_price, 0),
    COALESCE(p.default_commission_rate, 0),
    p.factory_id,
    p.product_category_id,
    p.product_uom_id,
    p.published,
    COALESCE(p.approval_needed, false),
    p.description,
    p.creation_type,
    COALESCE(p.entry_date, now()),
    p.created_by,
    p.individual_upc,  -- Map individual_upc to upc
    NULL,  -- default_divisor not in v5
    p.min_order_qty,
    CASE
        WHEN p.lead_time ~ '^\d+$' THEN p.lead_time::integer
        ELSE NULL
    END AS lead_time,  -- Convert varchar to integer
    p.overall_discount_rate,  -- Map overall_discount_rate to unit_price_discount_rate
    p.commission_discount_rate,
    p.approval_date,
    p.approval_comments,
    NULL  -- No tags in v5
FROM core.products p
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
