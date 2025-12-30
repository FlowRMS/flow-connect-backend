-- Migration: Product Quantity Pricing from v5 (core.product_quantity_pricing) to v6 (pycore.product_quantity_pricing)
-- Run order: 09
-- Dependencies: 07_migrate_products.sql

-- v5 schema: core.product_quantity_pricing (id, product_id, quantity_low, quantity_high, unit_price, commission_rate)
-- v6 schema: pycore.product_quantity_pricing (quantity_low, quantity_high, unit_price, commission_rate, product_id, id)

INSERT INTO pycore.product_quantity_pricing (
    id,
    quantity_low,
    quantity_high,
    unit_price,
    commission_rate,
    product_id
)
SELECT
    pqp.id,
    pqp.quantity_low,
    pqp.quantity_high,
    COALESCE(pqp.unit_price, 0),
    pqp.commission_rate,
    pqp.product_id
FROM core.product_quantity_pricing pqp
ON CONFLICT (id) DO UPDATE SET
    quantity_low = EXCLUDED.quantity_low,
    quantity_high = EXCLUDED.quantity_high,
    unit_price = EXCLUDED.unit_price,
    commission_rate = EXCLUDED.commission_rate,
    product_id = EXCLUDED.product_id;
