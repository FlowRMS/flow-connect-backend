-- Migration: Customer Factory Sales Reps from v4 (public.sales_rep_selection + default_outside_rep_split) to v6 (pycore.customer_factory_sales_reps)
-- Run order: 10
-- Dependencies: 01_migrate_users.sql, 02_migrate_customers.sql, 03_migrate_factories.sql

-- v4 schema: public.sales_rep_selection (id, customer, factory, create_date, created_by, customer_selection_type)
-- v4 schema: public.default_outside_rep_split (id, user_id, split_rate, create_date, selection_id, created_by)
-- v6 schema: pycore.customer_factory_sales_reps (customer_id, factory_id, user_id, split_rate, rep_type, position, id, created_at)

-- Note: v4 customer and factory are integers, need to map via uuid
-- We join sales_rep_selection with default_outside_rep_split to get the user assignments

INSERT INTO pycore.customer_factory_sales_reps (
    id,
    customer_id,
    factory_id,
    user_id,
    split_rate,
    rep_type,
    "position",
    created_at
)
SELECT
    dors.id,
    c.uuid,  -- Map integer customer to customer's uuid
    f.uuid,  -- Map integer factory to factory's uuid
    dors.user_id,
    COALESCE(dors.split_rate, 0),
    1,  -- OUTSIDE rep type (default_outside_rep_split)
    0,  -- Default position
    COALESCE(dors.create_date, now())
FROM public.default_outside_rep_split dors
JOIN public.sales_rep_selection srs ON dors.selection_id = srs.id
JOIN public.customers c ON srs.customer = c.customer_id
JOIN public.factories f ON srs.factory = f.factory_id
WHERE dors.user_id IS NOT NULL
ON CONFLICT (id) DO UPDATE SET
    customer_id = EXCLUDED.customer_id,
    factory_id = EXCLUDED.factory_id,
    user_id = EXCLUDED.user_id,
    split_rate = EXCLUDED.split_rate,
    rep_type = EXCLUDED.rep_type,
    "position" = EXCLUDED."position";
