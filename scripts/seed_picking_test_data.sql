-- =============================================================================
-- PICKING Test Data Seed Script (Dev A)
-- =============================================================================
-- Purpose: Create test data for PICKING status testing
-- Creates fulfillment order in PICKING status with inventory for testing:
--   - A1: Real inventory locations display
--   - A2: Split pick allocation (multiple locations)
--   - A3: Shortage detection alert
--   - A4: Report Backorder button
--
-- Usage:
--   psql -h <host> -U <user> -d <database> -f seed_picking_test_data.sql
-- =============================================================================

BEGIN;

DO $$
DECLARE
    v_factory_id UUID;
    v_company_id UUID;
    v_customer_id UUID;
    v_user_id UUID;
    v_warehouse_id UUID;
    v_location_section_id UUID;
    v_location_aisle_a_id UUID;
    v_location_aisle_b_id UUID;
    v_location_shelf_a1_id UUID;
    v_location_shelf_a2_id UUID;
    v_location_shelf_b1_id UUID;
    v_product_1_id UUID;
    v_product_2_id UUID;
    v_product_3_id UUID;
    v_inventory_1_id UUID;
    v_inventory_2_id UUID;
    v_inventory_3_id UUID;
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
    -- Get existing Warehouse Locations
    -- =============================================================================
    SELECT id INTO v_location_shelf_a1_id FROM pywarehouse.warehouse_locations
    WHERE warehouse_id = v_warehouse_id AND code = 'SHELF-A1' LIMIT 1;

    SELECT id INTO v_location_shelf_a2_id FROM pywarehouse.warehouse_locations
    WHERE warehouse_id = v_warehouse_id AND code = 'SHELF-A2' LIMIT 1;

    SELECT id INTO v_location_shelf_b1_id FROM pywarehouse.warehouse_locations
    WHERE warehouse_id = v_warehouse_id AND code = 'SHELF-B1' LIMIT 1;

    IF v_location_shelf_a1_id IS NULL THEN
        RAISE EXCEPTION 'Warehouse locations not found. Run seed_fulfillment_test_data.sql first.';
    END IF;

    RAISE NOTICE 'Locations: ShelfA1=%, ShelfA2=%, ShelfB1=%', v_location_shelf_a1_id, v_location_shelf_a2_id, v_location_shelf_b1_id;

    -- =============================================================================
    -- Get existing Test Products
    -- =============================================================================
    SELECT id INTO v_product_1_id FROM pycore.products WHERE factory_part_number = 'TEST-PROD-001' AND factory_id = v_factory_id;
    SELECT id INTO v_product_2_id FROM pycore.products WHERE factory_part_number = 'TEST-PROD-002' AND factory_id = v_factory_id;
    SELECT id INTO v_product_3_id FROM pycore.products WHERE factory_part_number = 'TEST-PROD-003' AND factory_id = v_factory_id;

    IF v_product_1_id IS NULL THEN
        RAISE EXCEPTION 'Test products not found. Run seed_fulfillment_test_data.sql first.';
    END IF;

    RAISE NOTICE 'Products: %, %, %', v_product_1_id, v_product_2_id, v_product_3_id;

    -- =============================================================================
    -- Get existing Inventory Records
    -- =============================================================================
    SELECT id INTO v_inventory_1_id FROM pywarehouse.inventory WHERE product_id = v_product_1_id AND warehouse_id = v_warehouse_id;
    SELECT id INTO v_inventory_2_id FROM pywarehouse.inventory WHERE product_id = v_product_2_id AND warehouse_id = v_warehouse_id;
    SELECT id INTO v_inventory_3_id FROM pywarehouse.inventory WHERE product_id = v_product_3_id AND warehouse_id = v_warehouse_id;

    IF v_inventory_1_id IS NULL THEN
        RAISE EXCEPTION 'Inventory not found. Run seed_fulfillment_test_data.sql first.';
    END IF;

    RAISE NOTICE 'Inventory: %, %, %', v_inventory_1_id, v_inventory_2_id, v_inventory_3_id;

    -- =============================================================================
    -- Create Order with Balance
    -- =============================================================================
    v_order_id := gen_random_uuid();
    v_balance_id := gen_random_uuid();

    INSERT INTO pycommission.order_balances (id, quantity, subtotal, total, commission, discount, discount_rate, commission_rate, commission_discount, commission_discount_rate, shipping_balance, cancelled_balance, freight_charge_balance)
    VALUES (v_balance_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);

    INSERT INTO pycommission.orders (
        id, order_number, entity_date, due_date, sold_to_customer_id, factory_id,
        balance_id, status, order_type, header_status, creation_type, published,
        created_by_id, created_at
    )
    VALUES (
        v_order_id,
        'PICK-TEST-' || TO_CHAR(NOW(), 'YYYYMMDD-HH24MISS'),
        CURRENT_DATE,
        CURRENT_DATE + INTERVAL '30 days',
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
    INSERT INTO pycommission.order_details (id, order_id, item_number, product_id, quantity, unit_price, subtotal, total, total_line_commission, commission_rate, commission, commission_discount_rate, commission_discount, discount_rate, discount)
    VALUES
        -- Product 1: 25 ordered - for split pick test (A-1 has 50, A-2 has 30)
        (gen_random_uuid(), v_order_id, 1, v_product_1_id, 25, 99.99, 2499.75, 2499.75, 0, 0, 0, 0, 0, 0, 0),
        -- Product 2: 10 ordered - simple pick from B-1 (has 50)
        (gen_random_uuid(), v_order_id, 2, v_product_2_id, 10, 149.99, 1499.90, 1499.90, 0, 0, 0, 0, 0, 0, 0),
        -- Product 3: 30 ordered but only 25 available - SHORTAGE TEST!
        (gen_random_uuid(), v_order_id, 3, v_product_3_id, 30, 79.99, 2399.70, 2399.70, 0, 0, 0, 0, 0, 0, 0);

    RAISE NOTICE 'Created order details';

    -- =============================================================================
    -- Create Fulfillment Order in PICKING STATUS
    -- =============================================================================
    v_fulfillment_order_id := gen_random_uuid();

    INSERT INTO pywarehouse.fulfillment_orders (
        id, fulfillment_order_number, order_id, warehouse_id, status,
        fulfillment_method, ship_to_address, need_by_date, has_backorder_items,
        tracking_numbers, released_at, pick_started_at, created_by_id, created_at
    )
    VALUES (
        v_fulfillment_order_id,
        'FO-PICK-' || TO_CHAR(NOW(), 'YYYYMMDD-HH24MISS'),
        v_order_id,
        v_warehouse_id,
        3,  -- PICKING status
        1,  -- SHIP
        '{"name": "Dev A Tester", "street": "123 Picking Lane", "city": "Austin", "state": "TX", "zip": "78701", "country": "USA"}',
        CURRENT_DATE + INTERVAL '7 days',
        false,
        '{}',
        NOW() - INTERVAL '1 hour',  -- released 1 hour ago
        NOW(),  -- picking just started
        v_user_id,
        NOW()
    );

    RAISE NOTICE 'Fulfillment Order ID: %', v_fulfillment_order_id;

    -- =============================================================================
    -- Create Fulfillment Order Line Items
    -- =============================================================================
    INSERT INTO pywarehouse.fulfillment_order_line_items (
        id, fulfillment_order_id, product_id,
        ordered_qty, allocated_qty, picked_qty, packed_qty, shipped_qty, backorder_qty,
        fulfilled_by_manufacturer
    )
    VALUES
        -- Product 1: 25 allocated, 0 picked (for testing picking)
        (gen_random_uuid(), v_fulfillment_order_id, v_product_1_id, 25, 25, 0, 0, 0, 0, false),
        -- Product 2: 10 allocated, 0 picked
        (gen_random_uuid(), v_fulfillment_order_id, v_product_2_id, 10, 10, 0, 0, 0, 0, false),
        -- Product 3: 30 ordered, 25 allocated, 5 backorder (shortage!)
        (gen_random_uuid(), v_fulfillment_order_id, v_product_3_id, 30, 25, 0, 0, 0, 5, false);

    RAISE NOTICE 'Created fulfillment line items';

    -- =============================================================================
    -- Summary
    -- =============================================================================
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'PICKING TEST DATA CREATED SUCCESSFULLY';
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'Warehouse ID: %', v_warehouse_id;
    RAISE NOTICE 'Fulfillment Order ID: %', v_fulfillment_order_id;
    RAISE NOTICE 'Fulfillment Number: FO-PICK-...';
    RAISE NOTICE 'Status: PICKING (3)';
    RAISE NOTICE '';
    RAISE NOTICE 'TEST SCENARIOS:';
    RAISE NOTICE '  A1 - Real Locations: Expand line items to see SHELF-A1, SHELF-A2, SHELF-B1';
    RAISE NOTICE '  A2 - Split Pick: Product 1 (25 units) from Shelf A-1 (50) or A-2 (30)';
    RAISE NOTICE '  A3 - Shortage: Product 3 needs 30, only 25 available -> RED ALERT';
    RAISE NOTICE '  A4 - Report Backorder: Click button -> status changes to BACKORDER_REVIEW';
    RAISE NOTICE '=============================================================================';

END $$;

COMMIT;
