-- Migration: Quote Split Rates from v4 (public.quote_sales_rep_split) to v6 (pycrm.quote_split_rates)
-- Run order: 16
-- Dependencies: 01_migrate_users.sql, 15_migrate_quote_details.sql

-- v4 schema: public.quote_sales_rep_split (id, user_id, quote_detail_id, split_rate, create_date)
-- v6 schema: pycrm.quote_split_rates (quote_detail_id, user_id, split_rate, position, id, created_at)

-- Note: v4 quote_detail_id is integer, but we generated new UUIDs for quote_details
-- This migration requires a lookup from v4 quote_detail_id to the new v6 quote_detail uuid
-- We'll use a join approach based on quote_id and item_number

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
    qd_v6.id,  -- Get the v6 quote_detail uuid
    qsr.user_id,
    COALESCE(qsr.split_rate, 0),
    0,  -- Default position
    COALESCE(qsr.create_date, now())
FROM public.quote_sales_rep_split qsr
JOIN public.quote_details qd_v4 ON qsr.quote_detail_id = qd_v4.quote_detail_id
JOIN public.quotes q ON qd_v4.quote_id = q.quote_id
JOIN pycrm.quotes q_v6 ON q_v6.quote_number = q.quote_number
JOIN pycrm.quote_details qd_v6 ON qd_v6.quote_id = q_v6.id AND qd_v6.item_number = qd_v4.item_number
ON CONFLICT (id) DO UPDATE SET
    quote_detail_id = EXCLUDED.quote_detail_id,
    user_id = EXCLUDED.user_id,
    split_rate = EXCLUDED.split_rate,
    "position" = EXCLUDED."position";
