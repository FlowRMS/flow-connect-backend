-- Migration: Pre-Opportunities from v5 (crm.pre_opportunities) to v6 (pycrm.pre_opportunities)
-- Run order: 25
-- Dependencies: 01_migrate_users.sql, 02_migrate_customers.sql, 24_migrate_pre_opportunity_balances.sql

-- v5 schema: crm.pre_opportunities (id, entry_date, created_by, user_owner_ids, creation_type, status,
--            published, balance_id, entity_number, sold_to_customer_id, sold_to_customer_address_id,
--            bill_to_customer_id, bill_to_customer_address_id, job_id, payment_terms, customer_ref,
--            freight_terms, entity_date, exp_date, revise_date, accept_date, participant_ids)
-- v6 schema: pycrm.pre_opportunities (status, entity_number, entity_date, exp_date, revise_date, accept_date,
--            sold_to_customer_id, sold_to_customer_address_id, bill_to_customer_id, bill_to_customer_address_id,
--            job_id, balance_id, payment_terms, customer_ref, freight_terms, tags, id, created_at, created_by_id)

-- Note: v5 status is a varchar, v6 status is smallint

INSERT INTO pycrm.pre_opportunities (
    id,
    status,
    entity_number,
    entity_date,
    exp_date,
    revise_date,
    accept_date,
    sold_to_customer_id,
    sold_to_customer_address_id,
    bill_to_customer_id,
    bill_to_customer_address_id,
    job_id,
    balance_id,
    payment_terms,
    customer_ref,
    freight_terms,
    tags,
    created_at,
    created_by_id
)
SELECT
    po.id,
    CASE
        WHEN UPPER(po.status) = 'OPEN' THEN 0
        WHEN UPPER(po.status) = 'WON' THEN 1
        WHEN UPPER(po.status) = 'LOST' THEN 2
        WHEN UPPER(po.status) = 'CANCELLED' THEN 3
        ELSE 0  -- Default to OPEN
    END AS status,  -- Map varchar status to smallint
    po.entity_number,
    po.entity_date,
    po.exp_date,
    po.revise_date,
    po.accept_date,
    po.sold_to_customer_id,
    po.sold_to_customer_address_id,
    po.bill_to_customer_id,
    po.bill_to_customer_address_id,
    po.job_id,
    po.balance_id,
    po.payment_terms,
    po.customer_ref,
    po.freight_terms,
    NULL,  -- tags not in v5
    COALESCE(po.entry_date, now()),
    po.created_by
FROM crm.pre_opportunities po
ON CONFLICT (id) DO UPDATE SET
    status = EXCLUDED.status,
    entity_number = EXCLUDED.entity_number,
    entity_date = EXCLUDED.entity_date,
    exp_date = EXCLUDED.exp_date,
    revise_date = EXCLUDED.revise_date,
    accept_date = EXCLUDED.accept_date,
    sold_to_customer_id = EXCLUDED.sold_to_customer_id,
    sold_to_customer_address_id = EXCLUDED.sold_to_customer_address_id,
    bill_to_customer_id = EXCLUDED.bill_to_customer_id,
    bill_to_customer_address_id = EXCLUDED.bill_to_customer_address_id,
    job_id = EXCLUDED.job_id,
    balance_id = EXCLUDED.balance_id,
    payment_terms = EXCLUDED.payment_terms,
    customer_ref = EXCLUDED.customer_ref,
    freight_terms = EXCLUDED.freight_terms;
