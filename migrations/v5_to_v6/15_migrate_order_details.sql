-- Migration: Order Details from v5 (commission.order_details) to v6 (pycommission.order_details)
-- Run order: 15
-- Dependencies: 14_migrate_orders.sql, 07_migrate_products.sql

-- v5 schema: commission.order_details (id, order_id, status, quantity, total, unit_price, product_id,
--            commission_rate, commission, commission_discount_rate, commission_discount, discount_rate,
--            discount, item_number, end_user_id, lead_time, product_cpn_id, uom_multiply, uom_multiply_by,
--            subtotal, factory_id, note, ...)
-- v6 schema: pycommission.order_details (order_id, item_number, quantity, unit_price, subtotal, total,
--            total_line_commission, commission_rate, commission, commission_discount_rate, commission_discount,
--            discount_rate, discount, division_factor, product_id, product_name_adhoc, product_description_adhoc,
--            factory_id, end_user_id, uom_id, lead_time, note, status, freight_charge, shipping_balance,
--            cancelled_balance, id)

INSERT INTO pycommission.order_details (
    id,
    order_id,
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
    division_factor,
    product_id,
    product_name_adhoc,
    product_description_adhoc,
    factory_id,
    end_user_id,
    uom_id,
    lead_time,
    note,
    status,
    freight_charge,
    shipping_balance,
    cancelled_balance
)
SELECT
    od.id,
    od.order_id,
    od.item_number,
    COALESCE(od.quantity, 0),
    COALESCE(od.unit_price, 0),
    COALESCE(od.subtotal, 0),
    COALESCE(od.total, 0),
    COALESCE(od.commission, 0),  -- Map commission to total_line_commission
    COALESCE(od.commission_rate, 0),
    COALESCE(od.commission, 0),
    COALESCE(od.commission_discount_rate, 0),
    COALESCE(od.commission_discount, 0),
    COALESCE(od.discount_rate, 0),
    COALESCE(od.discount, 0),
    CASE
        WHEN od.uom_multiply AND od.uom_multiply_by > 0 THEN od.uom_multiply_by::numeric(18,6)
        ELSE NULL
    END AS division_factor,  -- Map uom_multiply_by to division_factor
    od.product_id,
    NULL,  -- product_name_adhoc not in v5
    NULL,  -- product_description_adhoc not in v5
    od.factory_id,
    od.end_user_id,
    NULL,  -- uom_id not directly mapped
    od.lead_time,
    od.note,
    od.status,
    0,  -- freight_charge not in v5
    0,  -- shipping_balance not in v5
    0   -- cancelled_balance not in v5
FROM commission.order_details od
ON CONFLICT (id) DO UPDATE SET
    order_id = EXCLUDED.order_id,
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
    division_factor = EXCLUDED.division_factor,
    product_id = EXCLUDED.product_id,
    factory_id = EXCLUDED.factory_id,
    end_user_id = EXCLUDED.end_user_id,
    lead_time = EXCLUDED.lead_time,
    note = EXCLUDED.note,
    status = EXCLUDED.status;
