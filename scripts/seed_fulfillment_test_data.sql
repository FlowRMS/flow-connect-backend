-- =============================================================================
-- Fulfillment Test Data Seed Script
-- =============================================================================
-- Purpose: Create test data for end-to-end fulfillment workflow testing
--
-- Prerequisites:
--   - Run against staging database
--   - Requires existing: factory, user records
--   - Tables must exist (run migrations first)
--
-- Usage:
--   psql -h <host> -U <user> -d <database> -f seed_fulfillment_test_data.sql
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
    -- Create Test Company
    -- =============================================================================
    SELECT id INTO v_company_id FROM pycrm.companies WHERE name = 'Test Fulfillment Customer' LIMIT 1;

    IF v_company_id IS NULL THEN
        v_company_id := gen_random_uuid();
        INSERT INTO pycrm.companies (id, name, company_source_type, created_by_id, created_at)
        VALUES (v_company_id, 'Test Fulfillment Customer', 1, v_user_id, NOW());
        RAISE NOTICE 'Created test company ID: %', v_company_id;
    ELSE
        RAISE NOTICE 'Using existing company ID: %', v_company_id;
    END IF;

    -- =============================================================================
    -- Create Test Customer (for orders)
    -- =============================================================================
    SELECT id INTO v_customer_id FROM pycore.customers WHERE company_name = 'Test Fulfillment Customer' LIMIT 1;

    IF v_customer_id IS NULL THEN
        v_customer_id := gen_random_uuid();
        INSERT INTO pycore.customers (id, company_name, published, is_parent, created_by_id, created_at)
        VALUES (v_customer_id, 'Test Fulfillment Customer', true, false, v_user_id, NOW());
        RAISE NOTICE 'Created test customer ID: %', v_customer_id;
    ELSE
        RAISE NOTICE 'Using existing customer ID: %', v_customer_id;
    END IF;

    -- =============================================================================
    -- Create Test Warehouse (no code column)
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
    -- Create Warehouse Locations
    -- =============================================================================
    -- Section A
    SELECT id INTO v_location_section_id FROM pywarehouse.warehouse_locations
    WHERE warehouse_id = v_warehouse_id AND code = 'SEC-A' LIMIT 1;

    IF v_location_section_id IS NULL THEN
        v_location_section_id := gen_random_uuid();
        INSERT INTO pywarehouse.warehouse_locations (id, warehouse_id, level, name, code, parent_id, is_active, sort_order, created_at)
        VALUES (v_location_section_id, v_warehouse_id, 1, 'Section A', 'SEC-A', NULL, true, 1, NOW());
    END IF;

    -- Aisle A
    SELECT id INTO v_location_aisle_a_id FROM pywarehouse.warehouse_locations
    WHERE warehouse_id = v_warehouse_id AND code = 'AISLE-A' LIMIT 1;

    IF v_location_aisle_a_id IS NULL THEN
        v_location_aisle_a_id := gen_random_uuid();
        INSERT INTO pywarehouse.warehouse_locations (id, warehouse_id, level, name, code, parent_id, is_active, sort_order, created_at)
        VALUES (v_location_aisle_a_id, v_warehouse_id, 2, 'Aisle A', 'AISLE-A', v_location_section_id, true, 1, NOW());
    END IF;

    -- Aisle B
    SELECT id INTO v_location_aisle_b_id FROM pywarehouse.warehouse_locations
    WHERE warehouse_id = v_warehouse_id AND code = 'AISLE-B' LIMIT 1;

    IF v_location_aisle_b_id IS NULL THEN
        v_location_aisle_b_id := gen_random_uuid();
        INSERT INTO pywarehouse.warehouse_locations (id, warehouse_id, level, name, code, parent_id, is_active, sort_order, created_at)
        VALUES (v_location_aisle_b_id, v_warehouse_id, 2, 'Aisle B', 'AISLE-B', v_location_section_id, true, 2, NOW());
    END IF;

    -- Shelf A-1
    SELECT id INTO v_location_shelf_a1_id FROM pywarehouse.warehouse_locations
    WHERE warehouse_id = v_warehouse_id AND code = 'SHELF-A1' LIMIT 1;

    IF v_location_shelf_a1_id IS NULL THEN
        v_location_shelf_a1_id := gen_random_uuid();
        INSERT INTO pywarehouse.warehouse_locations (id, warehouse_id, level, name, code, parent_id, is_active, sort_order, created_at)
        VALUES (v_location_shelf_a1_id, v_warehouse_id, 3, 'Shelf A-1', 'SHELF-A1', v_location_aisle_a_id, true, 1, NOW());
    END IF;

    -- Shelf A-2
    SELECT id INTO v_location_shelf_a2_id FROM pywarehouse.warehouse_locations
    WHERE warehouse_id = v_warehouse_id AND code = 'SHELF-A2' LIMIT 1;

    IF v_location_shelf_a2_id IS NULL THEN
        v_location_shelf_a2_id := gen_random_uuid();
        INSERT INTO pywarehouse.warehouse_locations (id, warehouse_id, level, name, code, parent_id, is_active, sort_order, created_at)
        VALUES (v_location_shelf_a2_id, v_warehouse_id, 3, 'Shelf A-2', 'SHELF-A2', v_location_aisle_a_id, true, 2, NOW());
    END IF;

    -- Shelf B-1
    SELECT id INTO v_location_shelf_b1_id FROM pywarehouse.warehouse_locations
    WHERE warehouse_id = v_warehouse_id AND code = 'SHELF-B1' LIMIT 1;

    IF v_location_shelf_b1_id IS NULL THEN
        v_location_shelf_b1_id := gen_random_uuid();
        INSERT INTO pywarehouse.warehouse_locations (id, warehouse_id, level, name, code, parent_id, is_active, sort_order, created_at)
        VALUES (v_location_shelf_b1_id, v_warehouse_id, 3, 'Shelf B-1', 'SHELF-B1', v_location_aisle_b_id, true, 1, NOW());
    END IF;

    RAISE NOTICE 'Locations: Section=%, AisleA=%, AisleB=%, ShelfA1=%, ShelfA2=%, ShelfB1=%',
        v_location_section_id, v_location_aisle_a_id, v_location_aisle_b_id, v_location_shelf_a1_id, v_location_shelf_a2_id, v_location_shelf_b1_id;

    -- =============================================================================
    -- Create Test Products
    -- =============================================================================
    SELECT id INTO v_product_1_id FROM pycore.products WHERE factory_part_number = 'TEST-PROD-001' AND factory_id = v_factory_id;
    SELECT id INTO v_product_2_id FROM pycore.products WHERE factory_part_number = 'TEST-PROD-002' AND factory_id = v_factory_id;
    SELECT id INTO v_product_3_id FROM pycore.products WHERE factory_part_number = 'TEST-PROD-003' AND factory_id = v_factory_id;

    IF v_product_1_id IS NULL THEN
        v_product_1_id := gen_random_uuid();
        INSERT INTO pycore.products (id, factory_id, factory_part_number, description, unit_price, default_commission_rate, published, creation_type, created_by_id, created_at)
        VALUES (v_product_1_id, v_factory_id, 'TEST-PROD-001', 'Test Product 1 - Widget Alpha', 99.99, 0.10, true, 0, v_user_id, NOW());
    END IF;

    IF v_product_2_id IS NULL THEN
        v_product_2_id := gen_random_uuid();
        INSERT INTO pycore.products (id, factory_id, factory_part_number, description, unit_price, default_commission_rate, published, creation_type, created_by_id, created_at)
        VALUES (v_product_2_id, v_factory_id, 'TEST-PROD-002', 'Test Product 2 - Widget Beta', 149.99, 0.10, true, 0, v_user_id, NOW());
    END IF;

    IF v_product_3_id IS NULL THEN
        v_product_3_id := gen_random_uuid();
        INSERT INTO pycore.products (id, factory_id, factory_part_number, description, unit_price, default_commission_rate, published, creation_type, created_by_id, created_at)
        VALUES (v_product_3_id, v_factory_id, 'TEST-PROD-003', 'Test Product 3 - Widget Gamma', 79.99, 0.10, true, 0, v_user_id, NOW());
    END IF;

    RAISE NOTICE 'Products: %, %, %', v_product_1_id, v_product_2_id, v_product_3_id;

    -- =============================================================================
    -- Create Inventory Records
    -- =============================================================================
    SELECT id INTO v_inventory_1_id FROM pywarehouse.inventory WHERE product_id = v_product_1_id AND warehouse_id = v_warehouse_id;
    SELECT id INTO v_inventory_2_id FROM pywarehouse.inventory WHERE product_id = v_product_2_id AND warehouse_id = v_warehouse_id;
    SELECT id INTO v_inventory_3_id FROM pywarehouse.inventory WHERE product_id = v_product_3_id AND warehouse_id = v_warehouse_id;

    IF v_inventory_1_id IS NULL THEN
        v_inventory_1_id := gen_random_uuid();
        INSERT INTO pywarehouse.inventory (id, product_id, warehouse_id, total_quantity, available_quantity, reserved_quantity, picking_quantity, ownership_type, created_by_id, created_at, updated_at)
        VALUES (v_inventory_1_id, v_product_1_id, v_warehouse_id, 100, 80, 20, 0, 1, v_user_id, NOW(), NOW());
    END IF;

    IF v_inventory_2_id IS NULL THEN
        v_inventory_2_id := gen_random_uuid();
        INSERT INTO pywarehouse.inventory (id, product_id, warehouse_id, total_quantity, available_quantity, reserved_quantity, picking_quantity, ownership_type, created_by_id, created_at, updated_at)
        VALUES (v_inventory_2_id, v_product_2_id, v_warehouse_id, 50, 50, 0, 0, 1, v_user_id, NOW(), NOW());
    END IF;

    IF v_inventory_3_id IS NULL THEN
        v_inventory_3_id := gen_random_uuid();
        INSERT INTO pywarehouse.inventory (id, product_id, warehouse_id, total_quantity, available_quantity, reserved_quantity, picking_quantity, ownership_type, created_by_id, created_at, updated_at)
        VALUES (v_inventory_3_id, v_product_3_id, v_warehouse_id, 25, 25, 0, 0, 1, v_user_id, NOW(), NOW());
    END IF;

    RAISE NOTICE 'Inventory: %, %, %', v_inventory_1_id, v_inventory_2_id, v_inventory_3_id;

    -- =============================================================================
    -- Create Inventory Items
    -- =============================================================================
    DELETE FROM pywarehouse.inventory_items WHERE inventory_id IN (v_inventory_1_id, v_inventory_2_id, v_inventory_3_id);

    -- Product 1: 50 + 30 available + 20 reserved = 100 total
    INSERT INTO pywarehouse.inventory_items (id, inventory_id, location_id, quantity, lot_number, status, received_date, created_by_id, created_at)
    VALUES
        (gen_random_uuid(), v_inventory_1_id, v_location_shelf_a1_id, 50, 'LOT-2024-001', 1, NOW() - INTERVAL '30 days', v_user_id, NOW()),
        (gen_random_uuid(), v_inventory_1_id, v_location_shelf_a2_id, 30, 'LOT-2024-002', 1, NOW() - INTERVAL '15 days', v_user_id, NOW()),
        (gen_random_uuid(), v_inventory_1_id, v_location_shelf_a1_id, 20, 'LOT-2024-003', 2, NOW() - INTERVAL '7 days', v_user_id, NOW());

    -- Product 2: 50 in one location
    INSERT INTO pywarehouse.inventory_items (id, inventory_id, location_id, quantity, lot_number, status, received_date, created_by_id, created_at)
    VALUES (gen_random_uuid(), v_inventory_2_id, v_location_shelf_b1_id, 50, 'LOT-2024-004', 1, NOW() - INTERVAL '10 days', v_user_id, NOW());

    -- Product 3: 15 + 10 = 25 total (split across locations)
    INSERT INTO pywarehouse.inventory_items (id, inventory_id, location_id, quantity, lot_number, status, received_date, created_by_id, created_at)
    VALUES
        (gen_random_uuid(), v_inventory_3_id, v_location_shelf_a1_id, 15, 'LOT-2024-005', 1, NOW() - INTERVAL '20 days', v_user_id, NOW()),
        (gen_random_uuid(), v_inventory_3_id, v_location_shelf_b1_id, 10, 'LOT-2024-006', 1, NOW() - INTERVAL '5 days', v_user_id, NOW());

    RAISE NOTICE 'Created inventory items';

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
        'TEST-ORD-' || TO_CHAR(NOW(), 'YYYYMMDD-HH24MISS'),
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
        (gen_random_uuid(), v_order_id, 1, v_product_1_id, 25, 99.99, 2499.75, 2499.75, 0, 0, 0, 0, 0, 0, 0),
        (gen_random_uuid(), v_order_id, 2, v_product_2_id, 10, 149.99, 1499.90, 1499.90, 0, 0, 0, 0, 0, 0, 0),
        (gen_random_uuid(), v_order_id, 3, v_product_3_id, 30, 79.99, 2399.70, 2399.70, 0, 0, 0, 0, 0, 0, 0);

    RAISE NOTICE 'Created order details';

    -- =============================================================================
    -- Create Fulfillment Order
    -- =============================================================================
    v_fulfillment_order_id := gen_random_uuid();

    INSERT INTO pywarehouse.fulfillment_orders (
        id, fulfillment_order_number, order_id, warehouse_id, status,
        fulfillment_method, ship_to_address, need_by_date, has_backorder_items,
        tracking_numbers, created_by_id, created_at
    )
    VALUES (
        v_fulfillment_order_id,
        'FO-' || TO_CHAR(NOW(), 'YYYYMMDD-HH24MISS'),
        v_order_id,
        v_warehouse_id,
        2,  -- RELEASED
        1,  -- SHIP
        '{"name": "John Doe", "street": "456 Customer Ave", "city": "Houston", "state": "TX", "zip": "77001", "country": "USA"}',
        CURRENT_DATE + INTERVAL '7 days',
        false,
        '{}',
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
        (gen_random_uuid(), v_fulfillment_order_id, v_product_1_id, 25, 25, 0, 0, 0, 0, false),
        (gen_random_uuid(), v_fulfillment_order_id, v_product_2_id, 10, 10, 0, 0, 0, 0, false),
        (gen_random_uuid(), v_fulfillment_order_id, v_product_3_id, 30, 25, 0, 0, 0, 5, false);

    RAISE NOTICE 'Created fulfillment line items';

    -- =============================================================================
    -- Summary
    -- =============================================================================
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'SEED DATA CREATED SUCCESSFULLY';
    RAISE NOTICE '=============================================================================';
    RAISE NOTICE 'Warehouse ID: %', v_warehouse_id;
    RAISE NOTICE 'Fulfillment Order ID: %', v_fulfillment_order_id;
    RAISE NOTICE '';
    RAISE NOTICE 'Test Scenarios:';
    RAISE NOTICE '  Product 1: Pick 25 from Shelf A-1 (has 50) or A-2 (has 30)';
    RAISE NOTICE '  Product 2: Pick 10 from Shelf B-1 (has 50)';
    RAISE NOTICE '  Product 3: Pick 25 from A-1 (15) + B-1 (10) - 5 backorder';
    RAISE NOTICE '=============================================================================';

END $$;

COMMIT;
