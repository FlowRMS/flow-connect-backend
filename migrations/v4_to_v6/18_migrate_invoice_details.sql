-- Migration: Invoice Details from v4 (public.invoice_details) to v6 (pycommission.invoice_details)
-- Run order: 18
-- Dependencies: 17_migrate_invoices.sql, 06_migrate_products.sql, 12_migrate_order_details.sql

-- v4 schema: public.invoice_details (invoice_detail_id, invoice_id, product_id, commission_discount, commission,
--            commission_rate, unit_price, total, discount, quantity_shipped, shipped_date, order_detail_id,
--            item_number, status, end_user, outside_rep_id, discount_rate, commission_discount_rate)
-- v6 schema: pycommission.invoice_details (invoice_id, item_number, quantity_shipped, unit_price, subtotal, total,
--            total_line_commission, commission_rate, commission, commission_discount_rate, commission_discount,
--            discount_rate, discount, product_id, order_detail_id, end_user_id, shipped_date, status, id)

-- Note: v4 uses integers, need to map via uuid
-- v4 doesn't have a uuid for invoice_details, so we generate one

INSERT INTO pycommission.invoice_details (
    id,
    invoice_id,
    item_number,
    quantity_shipped,
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
    order_detail_id,
    end_user_id,
    shipped_date,
    status
)
SELECT
    gen_random_uuid(),  -- Generate new uuid for invoice_details
    inv.uuid,  -- Map integer invoice_id to invoice's uuid
    id.item_number,
    COALESCE(id.quantity_shipped, 0),
    COALESCE(id.unit_price, 0),
    COALESCE(id.quantity_shipped * id.unit_price, 0),  -- Calculate subtotal
    COALESCE(id.total, 0),
    COALESCE(id.commission, 0),  -- Map commission to total_line_commission
    COALESCE(id.commission_rate, 0),
    COALESCE(id.commission, 0),
    COALESCE(id.commission_discount_rate, 0),
    COALESCE(id.commission_discount, 0),
    COALESCE(id.discount_rate, 0),
    COALESCE(id.discount, 0),
    p.uuid,  -- Map integer product_id to product's uuid
    NULL,  -- order_detail_id mapping requires lookup, handled separately if needed
    eu.uuid,  -- Map integer end_user to customer's uuid
    id.shipped_date,
    id.status
FROM public.invoice_details id
JOIN public.invoices inv ON id.invoice_id = inv.invoice_id
LEFT JOIN public.products p ON id.product_id = p.product_id
LEFT JOIN public.customers eu ON id.end_user = eu.customer_id;

-- Note: This doesn't use ON CONFLICT since we're generating new UUIDs
-- If you need to run this migration multiple times, truncate the table first
