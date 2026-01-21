-- Migration: Order Split Rates from v4 (public.order_sales_rep_split) to v6 (pycommission.order_split_rates)
-- Run order: 13
-- Dependencies: 01_migrate_users.sql, 12_migrate_order_details.sql

-- v4 schema: public.order_sales_rep_split (id, user_id, order_detail_id, split_rate, create_date)
-- v6 schema: pycommission.order_split_rates (order_detail_id, user_id, split_rate, position, id, created_at)

-- Note: v4 order_detail_id is integer, but we generated new UUIDs for order_details
-- This migration requires a lookup from v4 order_detail_id to the new v6 order_detail uuid
-- Since we used gen_random_uuid() for order_details, we need a different approach

-- IMPORTANT: This migration assumes you have a way to map v4 order_detail_id to v6 order_detail.id
-- One approach is to store the original v4 order_detail_id during order_details migration
-- For now, we'll use a direct join approach based on order_id and item_number

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
    od_v6.id,  -- Get the v6 order_detail uuid
    osr.user_id,
    COALESCE(osr.split_rate, 0),
    0,  -- Default position
    COALESCE(osr.create_date, now())
FROM public.order_sales_rep_split osr
JOIN public.order_details od_v4 ON osr.order_detail_id = od_v4.order_detail_id
JOIN public.orders o ON od_v4.order_id = o.order_id
JOIN pycommission.orders o_v6 ON o_v6.order_number = o.order_number
JOIN pycommission.order_details od_v6 ON od_v6.order_id = o_v6.id AND od_v6.item_number = od_v4.item_number
ON CONFLICT (id) DO UPDATE SET
    order_detail_id = EXCLUDED.order_detail_id,
    user_id = EXCLUDED.user_id,
    split_rate = EXCLUDED.split_rate,
    "position" = EXCLUDED."position";
