-- Migration script: crm.pre_opportunities -> pycrm.pre_opportunities
--
-- Old status (varchar): 'DRAFT', 'PENDING', 'APPROVED', 'REJECTED', 'CONVERTED'
-- New PreOpportunityStatus (IntEnum): DRAFT=1, PENDING=2, APPROVED=3, REJECTED=4, CONVERTED=5
--
-- Dropped fields from pre_opportunities:
--   - user_owner_ids, creation_type, published, participant_ids
--
-- Dropped fields from pre_opportunity_details:
--   - status, uom_multiply, uom_multiply_by, commission_rate, commission,
--   - commission_discount_rate, commission_discount, lost_reason_id, lost_reason_other, factory_id
--
-- Dropped fields from pre_opportunity_balances:
--   - commission_rate, commission, commission_discount_rate, commission_discount

BEGIN;

-- Step 1: Migrate pre_opportunity_balances first (parent of pre_opportunities)
INSERT INTO pycrm.pre_opportunity_balances (id, subtotal, total, quantity, discount, discount_rate)
SELECT
    b.id,
    COALESCE(b.subtotal, 0) AS subtotal,
    COALESCE(b.total, 0) AS total,
    COALESCE(b.quantity, 0)::numeric AS quantity,
    COALESCE(b.discount, 0) AS discount,
    COALESCE(b.discount_rate, 0) AS discount_rate
FROM crm.pre_opportunity_balances b
ON CONFLICT (id) DO NOTHING;

-- Step 2: Migrate pre_opportunities
INSERT INTO pycrm.pre_opportunities (
    id, created_at, created_by_id, status, entity_number, entity_date,
    exp_date, revise_date, accept_date,
    sold_to_customer_id, sold_to_customer_address_id,
    bill_to_customer_id, bill_to_customer_address_id,
    job_id, balance_id, payment_terms, customer_ref, freight_terms, tags
)
SELECT
    p.id,
    p.entry_date AT TIME ZONE 'UTC' AS created_at,
    p.created_by AS created_by_id,
    CASE p.status
        WHEN 'DRAFT' THEN 1
        WHEN 'PENDING' THEN 2
        WHEN 'APPROVED' THEN 3
        WHEN 'REJECTED' THEN 4
        WHEN 'CONVERTED' THEN 5
        ELSE 1  -- Default to DRAFT if unknown
    END AS status,
    p.entity_number,
    p.entity_date,
    p.exp_date,
    p.revise_date,
    p.accept_date,
    p.sold_to_customer_id,
    p.sold_to_customer_address_id,
    p.bill_to_customer_id,
    p.bill_to_customer_address_id,
    p.job_id,
    p.balance_id,
    p.payment_terms,
    p.customer_ref,
    p.freight_terms,
    NULL AS tags
FROM crm.pre_opportunities p
WHERE EXISTS (SELECT 1 FROM pycrm.pre_opportunity_balances pb WHERE pb.id = p.balance_id)
ON CONFLICT (id) DO NOTHING;

-- Step 3: Migrate pre_opportunity_details
INSERT INTO pycrm.pre_opportunity_details (
    id, pre_opportunity_id, quantity, item_number, unit_price,
    total, subtotal, discount_rate, discount,
    product_id, product_cpn_id, end_user_id, lead_time
)
SELECT
    d.id,
    d.pre_opportunity_id,
    d.quantity::numeric AS quantity,
    d.item_number,
    d.unit_price,
    d.total,
    COALESCE(d.subtotal, 0) AS subtotal,
    COALESCE(d.discount_rate, 0) AS discount_rate,
    COALESCE(d.discount, 0) AS discount,
    d.product_id,
    d.product_cpn_id,
    d.end_user_id,
    d.lead_time
FROM crm.pre_opportunity_details d
WHERE EXISTS (SELECT 1 FROM pycrm.pre_opportunities pp WHERE pp.id = d.pre_opportunity_id)
ON CONFLICT (id) DO NOTHING;

COMMIT;

-- Verification queries (run separately after migration)
-- SELECT COUNT(*) AS pycrm_balances_count FROM pycrm.pre_opportunity_balances;
-- SELECT COUNT(*) AS crm_balances_count FROM crm.pre_opportunity_balances;
-- SELECT COUNT(*) AS pycrm_pre_opps_count FROM pycrm.pre_opportunities;
-- SELECT COUNT(*) AS crm_pre_opps_count FROM crm.pre_opportunities;
-- SELECT COUNT(*) AS pycrm_details_count FROM pycrm.pre_opportunity_details;
-- SELECT COUNT(*) AS crm_details_count FROM crm.pre_opportunity_details;
