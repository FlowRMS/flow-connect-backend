-- Migration: Quotes from v4 (public.quotes) to v6 (pycrm.quotes)
-- Run order: 14
-- Dependencies: 01_migrate_users.sql, 02_migrate_customers.sql, 03_migrate_factories.sql

-- v4 schema: public.quotes (quote_id, accept_date, commission, commission_rate, create_date, customer_ref,
--            exp_date, freight_terms, job_name, lost_reason, payment_terms, total, quote_date, quote_number,
--            quote_type, revise_date, status, terms, total_items, update_date, customer, end_user, factory_id,
--            outside_rep_id, draft, created_by, updated_by, uuid, discount, commission_discount, creation_type,
--            blanket, user_uuids)
-- v6 schema: pycrm.quotes (quote_number, entity_date, sold_to_customer_id, bill_to_customer_id, published,
--            creation_type, status, pipeline_stage, payment_terms, customer_ref, freight_terms, exp_date,
--            revise_date, accept_date, blanket, duplicated_from, version_of, balance_id, id, created_by_id,
--            created_at, job_id)

-- Note: v4 customer and factory_id are integers, need to map via uuid

INSERT INTO pycrm.quotes (
    id,
    quote_number,
    entity_date,
    sold_to_customer_id,
    bill_to_customer_id,
    published,
    creation_type,
    status,
    pipeline_stage,
    payment_terms,
    customer_ref,
    freight_terms,
    exp_date,
    revise_date,
    accept_date,
    blanket,
    duplicated_from,
    version_of,
    balance_id,
    created_by_id,
    created_at,
    job_id
)
SELECT
    q.uuid,
    q.quote_number,
    COALESCE(q.quote_date, q.create_date),  -- Map quote_date to entity_date
    c.uuid,  -- Map integer customer to customer's uuid (sold_to)
    c.uuid,  -- Use same customer for bill_to (v4 doesn't separate them)
    NOT COALESCE(q.draft, false),  -- Inverse of draft = published
    q.creation_type,
    q.status,
    0,  -- Default pipeline_stage to 0
    q.payment_terms,
    q.customer_ref,
    q.freight_terms,
    q.exp_date,
    q.revise_date,
    q.accept_date,
    COALESCE(q.blanket, false),
    NULL,  -- duplicated_from not in v4
    NULL,  -- version_of not in v4
    NULL,  -- balance_id not in v4 quotes table
    q.created_by,
    COALESCE(q.create_date, now()),
    NULL   -- job_id not in v4
FROM public.quotes q
LEFT JOIN public.customers c ON q.customer = c.customer_id
ON CONFLICT (id) DO UPDATE SET
    quote_number = EXCLUDED.quote_number,
    entity_date = EXCLUDED.entity_date,
    sold_to_customer_id = EXCLUDED.sold_to_customer_id,
    bill_to_customer_id = EXCLUDED.bill_to_customer_id,
    published = EXCLUDED.published,
    creation_type = EXCLUDED.creation_type,
    status = EXCLUDED.status,
    payment_terms = EXCLUDED.payment_terms,
    customer_ref = EXCLUDED.customer_ref,
    freight_terms = EXCLUDED.freight_terms,
    exp_date = EXCLUDED.exp_date,
    revise_date = EXCLUDED.revise_date,
    accept_date = EXCLUDED.accept_date,
    blanket = EXCLUDED.blanket;
