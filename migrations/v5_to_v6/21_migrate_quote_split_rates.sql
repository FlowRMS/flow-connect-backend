-- Migration: Quote Split Rates from v5 (crm.quote_split_rates) to v6 (pycrm.quote_split_rates)
-- Run order: 21
-- Dependencies: 01_migrate_users.sql, 20_migrate_quote_details.sql

-- v5 schema: crm.quote_split_rates (id, entry_date, user_id, quote_detail_id, split_rate,
--            commission_amount, position, sales_amount, created_by)
-- v6 schema: pycrm.quote_split_rates (quote_detail_id, user_id, split_rate, position, id, created_at)

INSERT INTO pycrm.quote_split_rates (
    id,
    quote_detail_id,
    user_id,
    split_rate,
    "position",
    created_at
)
SELECT
    qsr.id,
    qsr.quote_detail_id,
    qsr.user_id,
    COALESCE(qsr.split_rate, 0),
    COALESCE(qsr."position", 0)::integer,
    COALESCE(qsr.entry_date, now())
FROM crm.quote_split_rates qsr
ON CONFLICT (id) DO UPDATE SET
    quote_detail_id = EXCLUDED.quote_detail_id,
    user_id = EXCLUDED.user_id,
    split_rate = EXCLUDED.split_rate,
    "position" = EXCLUDED."position";

-- Migrate quote inside reps from crm.quote_inside_reps to pycrm.quote_inside_reps
-- v5 schema: crm.quote_inside_reps (id, entry_date, user_id, quote_id)
-- v6 schema: pycrm.quote_inside_reps (user_id, split_rate, position, id, created_at, quote_detail_id)

-- Note: v5 has quote_id while v6 has quote_detail_id - need to join with quote_details
INSERT INTO pycrm.quote_inside_reps (
    id,
    quote_detail_id,
    user_id,
    split_rate,
    "position",
    created_at
)
SELECT
    qir.id,
    qd.id AS quote_detail_id,  -- Get first quote detail for the quote
    qir.user_id,
    0,  -- Default split_rate to 0
    0,  -- Default position to 0
    COALESCE(qir.entry_date, now())
FROM crm.quote_inside_reps qir
LEFT JOIN crm.quote_details qd ON qd.quote_id = qir.quote_id AND qd.item_number = 1
ON CONFLICT (id) DO UPDATE SET
    quote_detail_id = EXCLUDED.quote_detail_id,
    user_id = EXCLUDED.user_id;
