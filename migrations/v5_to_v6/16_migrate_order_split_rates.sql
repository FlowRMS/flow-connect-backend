-- Migration: Order Split Rates from v5 (commission.order_split_rates) to v6 (pycommission.order_split_rates)
-- Run order: 16
-- Dependencies: 01_migrate_users.sql, 15_migrate_order_details.sql

-- v5 schema: commission.order_split_rates (id, entry_date, user_id, order_detail_id, split_rate,
--            commission_amount, position, sales_amount, created_by)
-- v6 schema: pycommission.order_split_rates (order_detail_id, user_id, split_rate, position, id, created_at)

INSERT INTO pycommission.order_split_rates (
    id,
    order_detail_id,
    user_id,
    split_rate,
    "position",
    created_at
)
SELECT
    osr.id,
    osr.order_detail_id,
    osr.user_id,
    COALESCE(osr.split_rate, 0),
    COALESCE(osr."position", 0)::integer,
    COALESCE(osr.entry_date, now())
FROM commission.order_split_rates osr
ON CONFLICT (id) DO UPDATE SET
    order_detail_id = EXCLUDED.order_detail_id,
    user_id = EXCLUDED.user_id,
    split_rate = EXCLUDED.split_rate,
    "position" = EXCLUDED."position";

-- Migrate order inside reps from commission.order_inside_reps to pycommission.order_inside_reps
-- v5 schema: commission.order_inside_reps (id, entry_date, user_id, order_detail_id)
-- v6 schema: pycommission.order_inside_reps (user_id, split_rate, position, id, created_at, order_detail_id)

INSERT INTO pycommission.order_inside_reps (
    id,
    order_detail_id,
    user_id,
    split_rate,
    "position",
    created_at
)
SELECT
    oir.id,
    oir.order_detail_id,
    oir.user_id,
    0,  -- Default split_rate to 0
    0,  -- Default position to 0
    COALESCE(oir.entry_date, now())
FROM commission.order_inside_reps oir
ON CONFLICT (id) DO UPDATE SET
    order_detail_id = EXCLUDED.order_detail_id,
    user_id = EXCLUDED.user_id;
