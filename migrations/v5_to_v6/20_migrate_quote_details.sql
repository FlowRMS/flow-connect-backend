-- Migration: Quote Details from v5 (crm.quote_details) to v6 (pycrm.quote_details)
-- Run order: 20
-- Dependencies: 19_migrate_quotes.sql, 07_migrate_products.sql, 18_migrate_quote_lost_reasons.sql

-- v5 schema: crm.quote_details (id, quote_id, status, quantity, total, unit_price, product_id,
--            commission_rate, commission, commission_discount_rate, commission_discount, discount_rate,
--            discount, item_number, end_user_id, lead_time, lost_reason_id, lost_reason_other,
--            product_cpn_id, uom_multiply, uom_multiply_by, subtotal, factory_id, base_unit_price,
--            overage_commission, rep_share, level_rate, level_unit_price, overage_commission_rate,
--            base_commission_rate, note, base_commission)
-- v6 schema: pycrm.quote_details (quote_id, item_number, quantity, unit_price, subtotal, total,
--            total_line_commission, commission_rate, commission, commission_discount_rate, commission_discount,
--            discount_rate, discount, product_id, product_name_adhoc, product_description_adhoc, factory_id,
--            end_user_id, lead_time, note, status, lost_reason_id, id, uom_id, division_factor, order_id)

INSERT INTO pycrm.quote_details (
    id,
    quote_id,
    item_number,
    quantity,
    unit_price,
    subtotal,
    total,
    total_line_commission,
    commission_rate,
    commission,
    commission_discount_rate,
    commission_discount,
    discount_rate,
    discount,
    product_id,
    product_name_adhoc,
    product_description_adhoc,
    factory_id,
    end_user_id,
    lead_time,
    note,
    status,
    lost_reason_id,
    uom_id,
    division_factor,
    order_id
)
SELECT
    qd.id,
    qd.quote_id,
    qd.item_number,
    COALESCE(qd.quantity, 0),
    COALESCE(qd.unit_price, 0),
    COALESCE(qd.subtotal, 0),
    COALESCE(qd.total, 0),
    COALESCE(qd.commission, 0),  -- Map commission to total_line_commission
    COALESCE(qd.commission_rate, 0),
    COALESCE(qd.commission, 0),
    COALESCE(qd.commission_discount_rate, 0),
    COALESCE(qd.commission_discount, 0),
    COALESCE(qd.discount_rate, 0),
    COALESCE(qd.discount, 0),
    qd.product_id,
    NULL,  -- product_name_adhoc not in v5
    NULL,  -- product_description_adhoc not in v5
    qd.factory_id,
    qd.end_user_id,
    qd.lead_time,
    qd.note,
    qd.status,
    qd.lost_reason_id,
    NULL,  -- uom_id not directly mapped
    CASE
        WHEN qd.uom_multiply AND qd.uom_multiply_by > 0 THEN qd.uom_multiply_by::numeric(18,6)
        ELSE NULL
    END AS division_factor,  -- Map uom_multiply_by to division_factor
    NULL  -- order_id not in v5 quote_details
FROM crm.quote_details qd
ON CONFLICT (id) DO UPDATE SET
    quote_id = EXCLUDED.quote_id,
    item_number = EXCLUDED.item_number,
    quantity = EXCLUDED.quantity,
    unit_price = EXCLUDED.unit_price,
    subtotal = EXCLUDED.subtotal,
    total = EXCLUDED.total,
    total_line_commission = EXCLUDED.total_line_commission,
    commission_rate = EXCLUDED.commission_rate,
    commission = EXCLUDED.commission,
    commission_discount_rate = EXCLUDED.commission_discount_rate,
    commission_discount = EXCLUDED.commission_discount,
    discount_rate = EXCLUDED.discount_rate,
    discount = EXCLUDED.discount,
    product_id = EXCLUDED.product_id,
    factory_id = EXCLUDED.factory_id,
    end_user_id = EXCLUDED.end_user_id,
    lead_time = EXCLUDED.lead_time,
    note = EXCLUDED.note,
    status = EXCLUDED.status,
    lost_reason_id = EXCLUDED.lost_reason_id,
    division_factor = EXCLUDED.division_factor;
