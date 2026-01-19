-- Fix order status values that were migrated with v4 values instead of v6 IntEnum values
--
-- v4 order_status:
--     1 = Open
--     2 = Partial Shipped
--     3 = Shipped Complete
--     5 = Needs Reconciling
--     6 = Paid - Matched
--     7 = Over Shipped
--     8 = Cancelled
--
-- v6 OrderStatus (IntEnum with auto() starting at 1):
--     1 = OPEN
--     2 = PARTIAL_SHIPPED
--     3 = SHIPPED_COMPLETE
--     4 = CANCELLED
--     5 = OVER_SHIPPED
--     6 = PARTIAL_CANCELLED
--     7 = OVER_CANCELLED

-- Update orders with incorrect status values
-- Note: v4 status 1, 2, 3 map to the same v6 values (1, 2, 3) so no change needed
-- Only status values 5, 6, 7, 8 need to be remapped

UPDATE pycommission.orders
SET status = CASE
    WHEN status = 5 THEN 1  -- Needs Reconciling -> OPEN
    WHEN status = 6 THEN 3  -- Paid - Matched -> SHIPPED_COMPLETE
    WHEN status = 7 THEN 5  -- Over Shipped -> OVER_SHIPPED
    WHEN status = 8 THEN 4  -- Cancelled -> CANCELLED
    ELSE status
END
WHERE status IN (5, 6, 7, 8);
