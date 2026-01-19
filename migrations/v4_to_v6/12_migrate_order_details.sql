-- Migration: Order Details from v4 (public.order_details) to v6 (pycommission.order_details)
-- Run order: 12
-- Dependencies: 11_migrate_orders.sql, 06_migrate_products.sql

-- v4 schema: public.order_details (order_detail_id, commission, commission_rate, unit_price, total, quantity,
--            order_id, product_id, commission_discount, order_balance, commission_balance, quote_detail_id,
--            invoiceDetailAmount, invoiceDetailCommRate, invoiceDetailCommission, shipping_balance, item_number,
--            discount, commission_discount_rate, outside_rep_id, end_user, discount_rate, status, lead_time,
--            refund_amount, refund_quantity, refund_commission_amount)
-- v6 schema: pycommission.order_details (order_id, item_number, quantity, unit_price, subtotal, total,
--            total_line_commission, commission_rate, commission, commission_discount_rate, commission_discount,
--            discount_rate, discount, division_factor, product_id, product_name_adhoc, product_description_adhoc,
--            factory_id, end_user_id, uom_id, lead_time, note, status, freight_charge, shipping_balance,
--            cancelled_balance, id)

-- Note: v4 uses integer order_id and product_id, need to map via uuid
-- v4 doesn't have a uuid for order_details, so we generate one

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
    gen_random_uuid(),  -- Generate new uuid for order_details
    o.uuid,  -- Map integer order_id to order's uuid
    od.item_number,
    COALESCE(od.quantity, 0),
    COALESCE(od.unit_price, 0),
    COALESCE(od.quantity * od.unit_price, 0),  -- Calculate subtotal
    COALESCE(od.total, 0),
    COALESCE(od.commission, 0),  -- Map commission to total_line_commission
    COALESCE(od.commission_rate, 0),
    COALESCE(od.commission, 0),
    COALESCE(od.commission_discount_rate, 0),
    COALESCE(od.commission_discount, 0),
    COALESCE(od.discount_rate, 0),
    COALESCE(od.discount, 0),
    NULL,  -- division_factor not in v4
    p.uuid,  -- Map integer product_id to product's uuid
    NULL,  -- product_name_adhoc not in v4
    NULL,  -- product_description_adhoc not in v4
    f.uuid,  -- Get factory_id from order
    eu.uuid,  -- Map integer end_user to customer's uuid
    NULL,  -- uom_id not in v4 order_details
    od.lead_time,
    NULL,  -- note not in v4
    od.status,
    0,  -- freight_charge not in v4
    COALESCE(od.shipping_balance, 0),
    0   -- cancelled_balance not in v4
FROM public.order_details od
JOIN public.orders o ON od.order_id = o.order_id
LEFT JOIN public.products p ON od.product_id = p.product_id
LEFT JOIN public.factories f ON o.factory_id = f.factory_id
LEFT JOIN public.customers eu ON od.end_user = eu.customer_id;

-- Note: This doesn't use ON CONFLICT since we're generating new UUIDs
-- If you need to run this migration multiple times, truncate the table first
