-- Migration: Invoices from v4 (public.invoices) to v6 (pycommission.invoices)
-- Run order: 17
-- Dependencies: 01_migrate_users.sql, 02_migrate_customers.sql, 03_migrate_factories.sql, 11_migrate_orders.sql

-- v4 schema: public.invoices (invoice_id, create_date, due_date, invoice_date, invoice_number, status, order_id,
--            factory_id, totalItemsCount, quantity_shipped, shippingBalance, customerName, closed, paid, locked,
--            updateDate, invoice_type, customer_id, import_id, uuid, draft, created_by, updatedBy, batch_id,
--            creation_type, invoice_amount, commission_rate, commission, paid_amount, commission_paid_amount)
-- v6 schema: pycommission.invoices (invoice_number, entity_date, due_date, status, invoice_type, total,
--            commission, commission_rate, paid_amount, commission_paid_amount, published, creation_type,
--            order_id, factory_id, customer_id, balance_id, id, created_by_id, created_at, batch_id)

INSERT INTO pycommission.invoices (
    id,
    invoice_number,
    entity_date,
    due_date,
    status,
    invoice_type,
    total,
    commission,
    commission_rate,
    paid_amount,
    commission_paid_amount,
    published,
    creation_type,
    order_id,
    factory_id,
    customer_id,
    balance_id,
    created_by_id,
    created_at,
    batch_id
)
SELECT
    i.uuid,
    i.invoice_number,
    COALESCE(i.invoice_date, i.create_date),  -- Map invoice_date to entity_date
    i.due_date,
    i.status,
    i.invoice_type,
    COALESCE(i.invoice_amount, 0),  -- Map invoice_amount to total
    COALESCE(i.commission, 0),
    COALESCE(i.commission_rate, 0),
    COALESCE(i.paid_amount, 0),
    COALESCE(i.commission_paid_amount, 0),
    NOT COALESCE(i.draft, false),  -- Inverse of draft = published
    i.creation_type,
    o.uuid,  -- Map integer order_id to order's uuid
    f.uuid,  -- Map integer factory_id to factory's uuid
    c.uuid,  -- Map integer customer_id to customer's uuid
    NULL,  -- balance_id not in v4
    i.created_by,
    COALESCE(i.create_date, now()),
    i.batch_id
FROM public.invoices i
LEFT JOIN public.orders o ON i.order_id = o.order_id
LEFT JOIN public.factories f ON i.factory_id = f.factory_id
LEFT JOIN public.customers c ON i.customer_id = c.customer_id
ON CONFLICT (id) DO UPDATE SET
    invoice_number = EXCLUDED.invoice_number,
    entity_date = EXCLUDED.entity_date,
    due_date = EXCLUDED.due_date,
    status = EXCLUDED.status,
    invoice_type = EXCLUDED.invoice_type,
    total = EXCLUDED.total,
    commission = EXCLUDED.commission,
    commission_rate = EXCLUDED.commission_rate,
    paid_amount = EXCLUDED.paid_amount,
    commission_paid_amount = EXCLUDED.commission_paid_amount,
    published = EXCLUDED.published,
    creation_type = EXCLUDED.creation_type,
    order_id = EXCLUDED.order_id,
    factory_id = EXCLUDED.factory_id,
    customer_id = EXCLUDED.customer_id;
