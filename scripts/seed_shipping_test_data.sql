-- =============================================================================
-- SHIPPING Test Data Seed Script (Dev A)
-- =============================================================================
-- Purpose: Create test data for SHIPPING status testing (A7, A8)
-- Creates fulfillment order in SHIPPING status WITH CARRIER for testing:
--   - A7: Tracking number entry and save
--   - A8: Ship confirmation modal
--
-- Usage:
--   psql -h <host> -U <user> -d <database> -f seed_shipping_test_data.sql
-- =============================================================================

BEGIN;

DO $$
DECLARE
    v_factory_id UUID;
    v_company_id UUID;
    v_customer_id UUID;
    v_user_id UUID;
    v_warehouse_id UUID;
    v_carrier_id UUID;
    v_product_1_id UUID;
    v_product_2_id UUID;
    v_order_id UUID;
    v_balance_id UUID;
    v_fulfillment_order_id UUID;
BEGIN
    -- Get first available factory
    SELECT id INTO v_factory_id FROM pycore.factories LIMIT 1;
    IF v_factory_id IS NULL THEN
        RAISE EXCEPTION 'No factory found. Please create a factory first.';
    END IF;
    RAISE NOTICE 'Using factory ID: %', v_factory_id;

    -- Get first available user
    SELECT id INTO v_user_id FROM pyuser.users LIMIT 1;
    IF v_user_id IS NULL THEN
        RAISE EXCEPTION 'No user found. Please create a user first.';
    END IF;
    RAISE NOTICE 'Using user ID: %', v_user_id;

    -- Get first available carrier
    SELECT id INTO v_carrier_id FROM pywarehouse.shipping_carriers LIMIT 1;
    IF v_carrier_id IS NULL THEN
        -- Create a test carrier
        v_carrier_id := gen_random_uuid();
        INSERT INTO pywarehouse.shipping_carriers (id, name, carrier_type, is_active, created_at)
        VALUES (v_carrier_id, 'UPS Ground', 1, true, NOW());
        RAISE NOTICE 'Created carrier ID: %', v_carrier_id;
    ELSE
        RAISE NOTICE 'Using existing carrier ID: %', v_carrier_id;
    END IF;

    -- =============================================================================
    -- Get or Create Test Company
    -- =============================================================================
    SELECT id INTO v_company_id FROM pycrm.companies WHERE name = 'Dev A Test Customer' LIMIT 1;

    IF v_company_id IS NULL THEN
        v_company_id := gen_random_uuid();
        INSERT INTO pycrm.companies (id, name, company_source_type, created_by_id, created_at)
        VALUES (v_company_id, 'Dev A Test Customer', 1, v_user_id, NOW());
        RAISE NOTICE 'Created test company ID: %', v_company_id;
    ELSE
        RAISE NOTICE 'Using existing company ID: %', v_company_id;
    END IF;

    -- =============================================================================
    -- Get or Create Test Customer
    -- =============================================================================
    SELECT id INTO v_customer_id FROM pycore.customers WHERE company_name = 'Dev A Test Customer' LIMIT 1;

    IF v_customer_id IS NULL THEN
        v_customer_id := gen_random_uuid();
        INSERT INTO pycore.customers (id, company_name, published, is_parent, created_by_id, created_at)
        VALUES (v_customer_id, 'Dev A Test Customer', true, false, v_user_id, NOW());
        RAISE NOTICE 'Created test customer ID: %', v_customer_id;
    ELSE
        RAISE NOTICE 'Using existing customer ID: %', v_customer_id;
    END IF;

    -- =============================================================================
    -- Get existing Test Warehouse
    -- =============================================================================
    SELECT id INTO v_warehouse_id FROM pywarehouse.warehouses WHERE name = 'Test Fulfillment Warehouse' LIMIT 1;

    IF v_warehouse_id IS NULL THEN
        v_warehouse_id := gen_random_uuid();
        INSERT INTO pywarehouse.warehouses (id, name, is_active, created_at)
        VALUES (v_warehouse_id, 'Test Fulfillment Warehouse', true, NOW());
        RAISE NOTICE 'Created warehouse ID: %', v_warehouse_id;
    ELSE
        RAISE NOTICE 'Using existing warehouse ID: %', v_warehouse_id;
    END IF;

    -- =============================================================================
    -- Get existing Products (use any available products)
    -- =============================================================================
    SELECT id INTO v_product_1_id FROM pycore.products WHERE factory_id = v_factory_id LIMIT 1;
    SELECT id INTO v_product_2_id FROM pycore.products WHERE factory_id = v_factory_id AND id != v_product_1_id LIMIT 1;

    IF v_product_1_id IS NULL THEN
        RAISE EXCEPTION 'No products found. Please create products first.';
    END IF;

    -- If only one product exists, use same for both
    IF v_product_2_id IS NULL THEN
        v_product_2_id := v_product_1_id;
    END IF;

    RAISE NOTICE 'Products: %, %', v_product_1_id, v_product_2_id;

    -- =============================================================================
    -- Create Order with Balance
    -- =============================================================================
    v_order_id := gen_random_uuid();
    v_balance_id := gen_random_uuid();

    INSERT INTO pycommission.order_balances (id, quantity, subtotal, total, commission, discount, discount_rate, commission_rate, commission_discount, commission_discount_rate, shipping_balance, cancelled_balance, freight_charge_balance)
    VALUES (v_balance_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

    INSERT INTO pycommission.orders (
        id, order_number, entity_date, due_date, entry_date, sold_to_customer_id, factory_id,
        balance_id, status, order_type, header_status, creation_type, published,
        created_by_id, created_at
    )
    VALUES (
        v_order_id,
        'SHIP-TEST-' || TO_CHAR(NOW(), 'YYYYMMDD-HH24MISS'),
        CURRENT_DATE,
        CURRENT_DATE + INTERVAL '30 days',
        CURRENT_DATE,  -- entry_date
        v_customer_id,
        v_factory_id,
        v_balance_id,
        1, 1, 1, 0, false,
        v_user_id,
        NOW()
    );

    RAISE NOTICE 'Order ID: %', v_order_id;

    -- =============================================================================
    -- Create Order Details
    -- =============================================================================
    INSERT INTO pycommission.order_details (id, order_id, item_number, product_id, quantity, unit_price, subtotal, total, total_line_commission, commission_rate, commission, commission_discount_rate, commission_discount, discount_rate, discount, freight_charge, status)
    VALUES
        (gen_random_uuid(), v_order_id, 1, v_product_1_id, 10, 99.99, 999.90, 999.90, 0, 0, 0, 0, 0, 0, 0, 0, 1),
        (gen_random_uuid(), v_order_id, 2, v_product_2_id, 5, 149.99, 749.95, 749.95, 0, 0, 0, 0, 0, 0, 0, 0, 1);

    RAISE NOTICE 'Created order details';

    -- =============================================================================
    -- Create Fulfillment Order in SHIPPING STATUS with CARRIER
    -- =============================================================================
    v_fulfillment_order_id := gen_random_uuid();

    INSERT INTO pywarehouse.fulfillment_orders (
        id, fulfillment_order_number, order_id, warehouse_id, carrier_id, carrier_type, status,
        fulfillment_method, ship_to_address, need_by_date, has_backorder_items,
        tracking_numbers, released_at, pick_started_at, pick_completed_at, pack_completed_at,
        created_by_id, created_at
    )
    VALUES (
        v_fulfillment_order_id,
        'FO-SHIP-' || TO_CHAR(NOW(), 'YYYYMMDD-HH24MISS'),
        v_order_id,
        v_warehouse_id,
        v_carrier_id,  -- CARRIER IS SET!
        1,  -- parcel
        5,  -- SHIPPING status
        1,  -- SHIP
        '{"name": "Dev A Tester", "street": "456 Shipping Blvd", "city": "Austin", "state": "TX", "zip": "78701", "country": "USA"}',
        CURRENT_DATE + INTERVAL '7 days',
        false,
        '{}',
        NOW() - INTERVAL '3 hours',  -- released
        NOW() - INTERVAL '2 hours',  -- picking started
        NOW() - INTERVAL '1 hour',   -- picking completed
        NOW() - INTERVAL '30 minutes',  -- packing completed
        v_user_id,
        NOW()
    );

    RAISE NOTICE 'Fulfillment Order ID: %', v_fulfillment_order_id;

    -- =============================================================================
    -- Create Fulfillment Order Line Items (fully picked and packed)
    -- =============================================================================
    INSERT INTO pywarehouse.fulfillment_order_line_items (
        id, fulfillment_order_id, product_id,
        ordered_qty, allocated_qty, picked_qty, packed_qty, shipped_qty, backorder_qty,
        fulfilled_by_manufacturer
    )
    VALUES
        (gen_random_uuid(), v_fulfillment_order_id, v_product_1_id, 10, 10, 10, 10, 0, 0, false),
        (gen_random_uuid(), v_fulfillment_order_id, v_product_2_id, 5, 5, 5, 5, 0, 0, false);

    RAISE NOTICE 'Created fulfillment line items';

    -- =============================================================================
    -- Summary
    -- =============================================================================
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'SHIPPING TEST DATA CREATED SUCCESSFULLY';
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'Warehouse ID: %', v_warehouse_id;
    RAISE NOTICE 'Carrier ID: %', v_carrier_id;
    RAISE NOTICE 'Fulfillment Order ID: %', v_fulfillment_order_id;
    RAISE NOTICE 'Fulfillment Number: FO-SHIP-...';
    RAISE NOTICE 'Status: SHIPPING (5)';
    RAISE NOTICE '';
    RAISE NOTICE 'TEST SCENARIOS:';
    RAISE NOTICE '  A7 - Tracking Number: Enter tracking number, should save to order';
    RAISE NOTICE '  A8 - Ship Confirmation: Click Confirm Shipment -> modal -> status to SHIPPED';
    RAISE NOTICE '=============================================================================';

END $$;

COMMIT;
