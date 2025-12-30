-- Migration: Pre-Opportunity Details from v5 (crm.pre_opportunity_details) to v6 (pycrm.pre_opportunity_details)
-- Run order: 26
-- Dependencies: 25_migrate_pre_opportunities.sql, 07_migrate_products.sql

-- v5 schema: crm.pre_opportunity_details (id, pre_opportunity_id, status, quantity, uom_multiply, uom_multiply_by,
--            total, unit_price, product_id, product_cpn_id, commission_rate, commission, commission_discount_rate,
--            commission_discount, discount_rate, discount, item_number, end_user_id, subtotal, lead_time,
--            lost_reason_id, lost_reason_other, factory_id)
-- v6 schema: pycrm.pre_opportunity_details (pre_opportunity_id, quantity, item_number, unit_price, total, subtotal,
--            discount_rate, discount, product_id, product_cpn_id, end_user_id, lead_time, id, quote_id)

-- Note: v6 has fewer fields - no commission-related columns, no status, no factory_id

INSERT INTO pycrm.pre_opportunity_details (
    id,
    pre_opportunity_id,
    quantity,
    item_number,
    unit_price,
    total,
    subtotal,
    discount_rate,
    discount,
    product_id,
    product_cpn_id,
    end_user_id,
    lead_time,
    quote_id
)
SELECT
    pod.id,
    pod.pre_opportunity_id,
    COALESCE(pod.quantity, 0),
    pod.item_number,
    COALESCE(pod.unit_price, 0),
    COALESCE(pod.total, 0),
    COALESCE(pod.subtotal, 0),
    COALESCE(pod.discount_rate, 0),
    COALESCE(pod.discount, 0),
    pod.product_id,
    pod.product_cpn_id,
    pod.end_user_id,
    pod.lead_time,
    NULL  -- quote_id not in v5
FROM crm.pre_opportunity_details pod
ON CONFLICT (id) DO UPDATE SET
    pre_opportunity_id = EXCLUDED.pre_opportunity_id,
    quantity = EXCLUDED.quantity,
    item_number = EXCLUDED.item_number,
    unit_price = EXCLUDED.unit_price,
    total = EXCLUDED.total,
    subtotal = EXCLUDED.subtotal,
    discount_rate = EXCLUDED.discount_rate,
    discount = EXCLUDED.discount,
    product_id = EXCLUDED.product_id,
    product_cpn_id = EXCLUDED.product_cpn_id,
    end_user_id = EXCLUDED.end_user_id,
    lead_time = EXCLUDED.lead_time;
