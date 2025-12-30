-- Migration: Product CPNs from v5 (core.product_cpns) to v6 (pycore.product_cpns)
-- Run order: 08
-- Dependencies: 02_migrate_customers.sql, 07_migrate_products.sql

-- v5 schema: core.product_cpns (id, product_id, customer_id, customer_part_number, unit_price, commission_rate)
-- v6 schema: pycore.product_cpns (customer_part_number, unit_price, commission_rate, product_id, customer_id, id)

INSERT INTO pycore.product_cpns (
    id,
    customer_part_number,
    unit_price,
    commission_rate,
    product_id,
    customer_id
)
SELECT
    c.id,
    c.customer_part_number,
    COALESCE(c.unit_price, 0),
    COALESCE(c.commission_rate, 0),
    c.product_id,
    c.customer_id
FROM core.product_cpns c
ON CONFLICT (id) DO UPDATE SET
    customer_part_number = EXCLUDED.customer_part_number,
    unit_price = EXCLUDED.unit_price,
    commission_rate = EXCLUDED.commission_rate,
    product_id = EXCLUDED.product_id,
    customer_id = EXCLUDED.customer_id;
