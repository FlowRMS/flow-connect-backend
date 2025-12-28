-- Migration: Customer Factory Sales Reps from v5 (core.sales_rep_selections) to v6 (pycore.customer_factory_sales_reps)
-- Run order: 12
-- Dependencies: 01_migrate_users.sql, 02_migrate_customers.sql, 04_migrate_factories.sql

-- v5 schema: core.sales_rep_selections (id, entry_date, created_by, creation_type, user_owner_ids, customer_id, factory_id)
--            core.sales_rep_selection_split_rates (id, entry_date, user_id, sales_pep_selection_id, split_rate, position)
-- v6 schema: pycore.customer_factory_sales_reps (id, customer_id, factory_id, user_id, rate, position, created_at)

-- Migrate from sales_rep_selection_split_rates joining with sales_rep_selections
INSERT INTO pycore.customer_factory_sales_reps (
    id,
    customer_id,
    factory_id,
    user_id,
    rate,
    "position",
    created_at
)
SELECT
    srssr.id,
    srs.customer_id,
    srs.factory_id,
    srssr.user_id,
    COALESCE(srssr.split_rate, 0),
    COALESCE(srssr."position", 0)::integer,
    COALESCE(srssr.entry_date, now())
FROM core.sales_rep_selection_split_rates srssr
JOIN core.sales_rep_selections srs ON srssr.sales_pep_selection_id = srs.id
ON CONFLICT (id) DO UPDATE SET
    customer_id = EXCLUDED.customer_id,
    factory_id = EXCLUDED.factory_id,
    user_id = EXCLUDED.user_id,
    rate = EXCLUDED.rate,
    "position" = EXCLUDED."position";
