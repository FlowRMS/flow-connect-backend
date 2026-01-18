-- Migration: Orders from v4 (public.orders) to v6 (pycommission.orders)
-- Run order: 11
-- Dependencies: 01_migrate_users.sql, 02_migrate_customers.sql, 03_migrate_factories.sql

-- v4 schema: public.orders (order_id, uuid, order_number, create_date, order_date, ship_date, revise_date,
--            due_date, status, fact_so_number, pro_number, payment_terms, freight_terms, job_name, customer_ref,
--            customer, factory_id, quote_id, reconciled, order_balance, created_by, quantity, commission_balance,
--            shipping_balance, order_type, commission_discount, discount, locked, import_id, draft, creation_type,
--            order_amount, commission_rate, commission, user_uuids, refund_amount, refund_quantity, refund_commission_amount)
-- v6 schema: pycommission.orders (order_number, entity_date, due_date, sold_to_customer_id, bill_to_customer_id,
--            published, creation_type, status, order_type, header_status, factory_id, shipping_terms,
--            freight_terms, mark_number, ship_date, projected_ship_date, fact_so_number, quote_id,
--            balance_id, id, created_by_id, created_at, job_id)

-- Note: v4 customer and factory_id are integers, need to map via uuid
-- Note: v4 doesn't have balance_id (separate balance table), so we'll set to NULL

INSERT INTO pycommission.orders (
    id,
    order_number,
    entity_date,
    due_date,
    sold_to_customer_id,
    bill_to_customer_id,
    published,
    creation_type,
    status,
    order_type,
    header_status,
    factory_id,
    shipping_terms,
    freight_terms,
    mark_number,
    ship_date,
    projected_ship_date,
    fact_so_number,
    quote_id,
    balance_id,
    created_by_id,
    created_at,
    job_id
)
SELECT
    o.uuid,
    o.order_number,
    COALESCE(o.order_date, o.create_date),  -- Map order_date to entity_date
    o.due_date,
    c.uuid,  -- Map integer customer to customer's uuid (sold_to)
    c.uuid,  -- Use same customer for bill_to (v4 doesn't separate them)
    NOT COALESCE(o.draft, false),  -- Inverse of draft = published
    o.creation_type,
    o.status,
    o.order_type,
    1,  -- Default header_status
    f.uuid,  -- Map integer factory_id to factory's uuid
    o.payment_terms,  -- Map payment_terms to shipping_terms
    o.freight_terms,
    o.pro_number,  -- Map pro_number to mark_number
    o.ship_date,
    NULL,  -- projected_ship_date not in v4
    o.fact_so_number,
    NULL,  -- quote_id needs uuid mapping, handled separately
    NULL,  -- balance_id not in v4 orders table
    o.created_by,
    COALESCE(o.create_date, now()),
    NULL   -- job_id not in v4
FROM public.orders o
LEFT JOIN public.customers c ON o.customer = c.customer_id
LEFT JOIN public.factories f ON o.factory_id = f.factory_id
ON CONFLICT (id) DO UPDATE SET
    order_number = EXCLUDED.order_number,
    entity_date = EXCLUDED.entity_date,
    due_date = EXCLUDED.due_date,
    sold_to_customer_id = EXCLUDED.sold_to_customer_id,
    bill_to_customer_id = EXCLUDED.bill_to_customer_id,
    published = EXCLUDED.published,
    creation_type = EXCLUDED.creation_type,
    status = EXCLUDED.status,
    order_type = EXCLUDED.order_type,
    header_status = EXCLUDED.header_status,
    factory_id = EXCLUDED.factory_id,
    shipping_terms = EXCLUDED.shipping_terms,
    freight_terms = EXCLUDED.freight_terms,
    mark_number = EXCLUDED.mark_number,
    ship_date = EXCLUDED.ship_date,
    fact_so_number = EXCLUDED.fact_so_number;
