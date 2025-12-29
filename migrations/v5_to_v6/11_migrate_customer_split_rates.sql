-- Migration: Customer Split Rates from v5 (core.customer_split_rates) to v6 (pycore.customer_split_rates)
-- Run order: 11
-- Dependencies: 01_migrate_users.sql, 02_migrate_customers.sql

-- v5 schema: core.customer_split_rates (id, entry_date, user_id, customer_id, split_rate, position)
-- v6 schema: pycore.customer_split_rates (user_id, customer_id, split_rate, rep_type, position, id, created_at)

-- Note: v6 has rep_type field (1=OUTSIDE, 2=INSIDE). Determine from user's inside/outside flags.
-- If user.inside=true, rep_type=2 (INSIDE), otherwise rep_type=1 (OUTSIDE)

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
    csr.customer_id,
    COALESCE(csr.split_rate, 0),
    CASE WHEN COALESCE(u.inside, false) = true THEN 2 ELSE 1 END,
    COALESCE(csr."position", 0)::integer,
    COALESCE(csr.entry_date, now())
FROM core.customer_split_rates csr
JOIN "user".users u ON u.id = csr.user_id
ON CONFLICT (id) DO UPDATE SET
    user_id = EXCLUDED.user_id,
    customer_id = EXCLUDED.customer_id,
    split_rate = EXCLUDED.split_rate,
    rep_type = EXCLUDED.rep_type,
    "position" = EXCLUDED."position";
