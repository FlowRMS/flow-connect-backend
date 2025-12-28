-- Migration: Orders from v5 (commission.orders) to v6 (pycommission.orders)
-- Run order: 14
-- Dependencies: 01_migrate_users.sql, 02_migrate_customers.sql, 04_migrate_factories.sql, 13_migrate_order_balances.sql

-- v5 schema: commission.orders (id, entry_date, created_by, creation_type, published, balance_id, status,
--            order_number, factory_id, sold_to_customer_id, job_name, shipping_terms, freight_terms,
--            mark_number, order_type, entity_date, ship_date, due_date, fact_so_number, quote_id,
--            user_owner_ids, job_id, sold_to_customer_address_id, bill_to_customer_id,
--            bill_to_customer_address_id, duplicated_from, transaction_type, header_status, ...)
-- v6 schema: pycommission.orders (order_number, entity_date, due_date, sold_to_customer_id, bill_to_customer_id,
--            published, creation_type, status, order_type, header_status, factory_id, shipping_terms,
--            freight_terms, mark_number, ship_date, projected_ship_date, fact_so_number, quote_id,
--            balance_id, id, created_by_id, created_at, job_id)

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
    o.id,
    o.order_number,
    o.entity_date,
    o.due_date,
    o.sold_to_customer_id,
    o.bill_to_customer_id,
    o.published,
    o.creation_type,
    o.status,
    o.order_type,
    COALESCE(o.header_status, 1),
    o.factory_id,
    o.shipping_terms,
    o.freight_terms,
    o.mark_number,
    o.ship_date,
    NULL,  -- projected_ship_date not in v5
    o.fact_so_number,
    o.quote_id,
    o.balance_id,
    o.created_by,
    COALESCE(o.entry_date, now()),
    o.job_id
FROM commission.orders o
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
    fact_so_number = EXCLUDED.fact_so_number,
    quote_id = EXCLUDED.quote_id,
    balance_id = EXCLUDED.balance_id,
    job_id = EXCLUDED.job_id;
