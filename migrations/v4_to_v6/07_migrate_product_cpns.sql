-- Migration: Product CPNs from v4 (public.product_cpn) to v6 (pycore.product_cpns)
-- Run order: 07
-- Dependencies: 02_migrate_customers.sql, 06_migrate_products.sql

-- v4 schema: public.product_cpn (product_cpn_id, product_id, customer_id, customer_part_number, unit_price, commission_rate, uuid)
-- v6 schema: pycore.product_cpns (customer_part_number, unit_price, commission_rate, product_id, customer_id, id)

-- Note: v4 uses integer product_id and customer_id, need to map via uuid

INSERT INTO pycore.product_cpns (
    id,
    customer_part_number,
    unit_price,
    commission_rate,
    product_id,
    customer_id
)
SELECT
    cpn.uuid,
    cpn.customer_part_number,
    COALESCE(cpn.unit_price, 0),
    COALESCE(cpn.commission_rate, 0),
    p.uuid,  -- Map integer product_id to product's uuid
    c.uuid   -- Map integer customer_id to customer's uuid
FROM public.product_cpn cpn
JOIN public.products p ON cpn.product_id = p.product_id
JOIN public.customers c ON cpn.customer_id = c.customer_id
ON CONFLICT (id) DO UPDATE SET
    customer_part_number = EXCLUDED.customer_part_number,
    unit_price = EXCLUDED.unit_price,
    commission_rate = EXCLUDED.commission_rate,
    product_id = EXCLUDED.product_id,
    customer_id = EXCLUDED.customer_id;
