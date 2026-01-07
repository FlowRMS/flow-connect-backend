-- Migration: Quotes from v5 (crm.quotes) to v6 (pycrm.quotes)
-- Run order: 19
-- Dependencies: 01_migrate_users.sql, 02_migrate_customers.sql, 17_migrate_quote_balances.sql

-- v5 schema: crm.quotes (id, entry_date, created_by, creation_type, status, published, balance_id,
--            quote_number, sold_to_customer_id, job_name, payment_terms, customer_ref, freight_terms,
--            entity_date, exp_date, revise_date, accept_date, blanket, user_owner_ids, job_id,
--            sold_to_customer_address_id, bill_to_customer_id, bill_to_customer_address_id, duplicated_from,
--            participant_ids)
-- v6 schema: pycrm.quotes (quote_number, entity_date, sold_to_customer_id, bill_to_customer_id, published,
--            creation_type, status, pipeline_stage, payment_terms, customer_ref, freight_terms, exp_date,
--            revise_date, accept_date, blanket, duplicated_from, version_of, balance_id, id, created_by_id,
--            created_at, job_id)

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
    q.id,
    q.quote_number,
    q.entity_date,
    q.sold_to_customer_id,
    q.bill_to_customer_id,
    q.published,
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
    q.duplicated_from,
    NULL,  -- version_of not in v5
    q.balance_id,
    q.created_by,
    COALESCE(q.entry_date, now()),
    q.job_id
FROM crm.quotes q
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
    blanket = EXCLUDED.blanket,
    duplicated_from = EXCLUDED.duplicated_from,
    balance_id = EXCLUDED.balance_id,
    job_id = EXCLUDED.job_id;
