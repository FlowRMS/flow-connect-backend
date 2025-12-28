-- Migration: Order Balances from v5 (commission.order_balances) to v6 (pycommission.order_balances)
-- Run order: 13
-- Dependencies: None

-- v5 schema: commission.order_balances (id, total, quantity, commission_rate, commission,
--            commission_discount_rate, commission_discount, subtotal, discount, discount_rate)
-- v6 schema: pycommission.order_balances (quantity, subtotal, total, commission, discount, discount_rate,
--            commission_rate, commission_discount, commission_discount_rate, shipping_balance,
--            cancelled_balance, freight_charge_balance, id)

INSERT INTO pycommission.order_balances (
    id,
    quantity,
    subtotal,
    total,
    commission,
    discount,
    discount_rate,
    commission_rate,
    commission_discount,
    commission_discount_rate,
    shipping_balance,
    cancelled_balance,
    freight_charge_balance
)
SELECT
    ob.id,
    COALESCE(ob.quantity, 0),
    COALESCE(ob.subtotal, 0),
    COALESCE(ob.total, 0),
    COALESCE(ob.commission, 0),
    COALESCE(ob.discount, 0),
    COALESCE(ob.discount_rate, 0),
    COALESCE(ob.commission_rate, 0),
    COALESCE(ob.commission_discount, 0),
    COALESCE(ob.commission_discount_rate, 0),
    0,  -- shipping_balance not in v5
    0,  -- cancelled_balance not in v5
    0   -- freight_charge_balance not in v5
FROM commission.order_balances ob
ON CONFLICT (id) DO UPDATE SET
    quantity = EXCLUDED.quantity,
    subtotal = EXCLUDED.subtotal,
    total = EXCLUDED.total,
    commission = EXCLUDED.commission,
    discount = EXCLUDED.discount,
    discount_rate = EXCLUDED.discount_rate,
    commission_rate = EXCLUDED.commission_rate,
    commission_discount = EXCLUDED.commission_discount,
    commission_discount_rate = EXCLUDED.commission_discount_rate;
