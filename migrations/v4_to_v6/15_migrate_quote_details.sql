-- Migration: Quote Details from v4 (public.quote_details) to v6 (pycrm.quote_details)
-- Run order: 15
-- Dependencies: 14_migrate_quotes.sql, 06_migrate_products.sql

-- v4 schema: public.quote_details (quote_detail_id, commission, commission_rate, unit_price, total, quantity,
--            product_id, quote_id, discount, item_number, end_user, commission_discount, commission_discount_rate,
--            discount_rate, outside_rep_id, status, lead_time, lost_reason, lost_reason_other)
-- v6 schema: pycrm.quote_details (quote_id, item_number, quantity, unit_price, subtotal, total,
--            total_line_commission, commission_rate, commission, commission_discount_rate, commission_discount,
--            discount_rate, discount, product_id, product_name_adhoc, product_description_adhoc, factory_id,
--            end_user_id, lead_time, note, status, lost_reason_id, id, uom_id, division_factor, order_id)

-- Note: v4 uses integer quote_id and product_id, need to map via uuid
-- v4 doesn't have a uuid for quote_details, so we generate one

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
    gen_random_uuid(),  -- Generate new uuid for quote_details
    q.uuid,  -- Map integer quote_id to quote's uuid
    qd.item_number,
    COALESCE(qd.quantity, 0),
    COALESCE(qd.unit_price, 0),
    COALESCE(qd.quantity * qd.unit_price, 0),  -- Calculate subtotal
    COALESCE(qd.total, 0),
    COALESCE(qd.commission, 0),  -- Map commission to total_line_commission
    COALESCE(qd.commission_rate, 0),
    COALESCE(qd.commission, 0),
    COALESCE(qd.commission_discount_rate, 0),
    COALESCE(qd.commission_discount, 0),
    COALESCE(qd.discount_rate, 0),
    COALESCE(qd.discount, 0),
    p.uuid,  -- Map integer product_id to product's uuid
    NULL,  -- product_name_adhoc not in v4
    NULL,  -- product_description_adhoc not in v4
    f.uuid,  -- Get factory_id from product's factory
    eu.uuid,  -- Map integer end_user to customer's uuid
    qd.lead_time,
    NULL,  -- note not in v4
    qd.status,
    qd.lost_reason,  -- lost_reason in v4 is uuid
    NULL,  -- uom_id not in v4 quote_details
    NULL,  -- division_factor not in v4
    NULL   -- order_id not in v4 quote_details
FROM public.quote_details qd
JOIN public.quotes q ON qd.quote_id = q.quote_id
LEFT JOIN public.products p ON qd.product_id = p.product_id
LEFT JOIN public.factories f ON p.factory_id = f.factory_id
LEFT JOIN public.customers eu ON qd.end_user = eu.customer_id;

-- Note: This doesn't use ON CONFLICT since we're generating new UUIDs
-- If you need to run this migration multiple times, truncate the table first
