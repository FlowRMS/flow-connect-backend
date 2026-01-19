-- Migration: Customer Split Rates from v4 (public.default_outside_rep_customer_split) to v6 (pycore.customer_split_rates)
-- Run order: 09
-- Dependencies: 01_migrate_users.sql, 02_migrate_customers.sql

-- v4 schema: public.default_outside_rep_customer_split (id, user_id, customer_id, split_rate, created_by, create_date)
-- v6 schema: pycore.customer_split_rates (user_id, customer_id, split_rate, rep_type, position, id, created_at)

-- Note: v4 customer_id is integer, need to map via customer's uuid
-- rep_type: 1=OUTSIDE, 2=INSIDE. Since this is "outside_rep" table, default to 1

INSERT INTO pycore.customer_split_rates (
    id,
    user_id,
    customer_id,
    split_rate,
    rep_type,
    "position",
    created_at
)
SELECT
    csr.id,
    csr.user_id,
    c.uuid,  -- Map integer customer_id to customer's uuid
    COALESCE(csr.split_rate, 0),
    1,  -- OUTSIDE rep type (from default_outside_rep_customer_split)
    0,  -- Default position
    COALESCE(csr.create_date, now())
FROM public.default_outside_rep_customer_split csr
JOIN public.customers c ON csr.customer_id = c.customer_id
ON CONFLICT (id) DO UPDATE SET
    user_id = EXCLUDED.user_id,
    customer_id = EXCLUDED.customer_id,
    split_rate = EXCLUDED.split_rate,
    rep_type = EXCLUDED.rep_type,
    "position" = EXCLUDED."position";
