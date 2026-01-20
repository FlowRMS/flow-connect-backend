-- Master Migration Script: v4 to v6
-- This script runs all migrations in the correct order
--
-- IMPORTANT: Review each migration file before running!
-- Some migrations may need adjustments based on your specific data.
--
-- Key differences from v4 to v6:
-- - v4 uses integer IDs (customer_id, factory_id, product_id, etc.) with separate UUID fields
-- - v6 uses UUID as the primary key (id)
-- - v4 schema is in 'public' schema
-- - v6 schema uses multiple schemas: pyuser, pycore, pycommission, pycrm, pyfiles
--
-- Run order:
-- 01. Users
-- 02. Customers
-- 03. Factories
-- 04. Product UOMs
-- 05. Product Categories
-- 06. Products
-- 07. Product CPNs
-- 08. Addresses
-- 09. Customer Split Rates
-- 10. Customer Factory Sales Reps
-- 11. Orders
-- 12. Order Details
-- 13. Order Split Rates
-- 14. Quotes
-- 15. Quote Details
-- 16. Quote Split Rates
-- 17. Invoices
-- 18. Invoice Details

-- Schema mapping summary:
-- v4 (public)                              -> v6
-- public.users                             -> pyuser.users
-- public.customers                         -> pycore.customers
-- public.factories                         -> pycore.factories
-- public.unit_of_measures                  -> pycore.product_uoms
-- public.product_categories                -> pycore.product_categories
-- public.products                          -> pycore.products
-- public.product_cpn                       -> pycore.product_cpns
-- public.addresses                         -> pycore.addresses
-- public.default_outside_rep_customer_split -> pycore.customer_split_rates
-- public.sales_rep_selection + default_outside_rep_split -> pycore.customer_factory_sales_reps
-- public.orders                            -> pycommission.orders
-- public.order_details                     -> pycommission.order_details
-- public.order_sales_rep_split             -> pycommission.order_split_rates
-- public.quotes                            -> pycrm.quotes
-- public.quote_details                     -> pycrm.quote_details
-- public.quote_sales_rep_split             -> pycrm.quote_split_rates
-- public.invoices                          -> pycommission.invoices
-- public.invoice_details                   -> pycommission.invoice_details

-- ID mapping notes:
-- - v4 uses integer IDs (customer_id, factory_id, etc.) with a separate uuid field
-- - v6 uses the uuid as the primary key (id)
-- - This migration maps v4 integer references to v6 uuid references via joins

-- To run all migrations, execute the individual files in order:
-- psql -f 01_migrate_users.sql
-- psql -f 02_migrate_customers.sql
-- ... etc

-- Or use this script to include all migrations inline:
-- \i 01_migrate_users.sql
-- \i 02_migrate_customers.sql
-- ... etc

BEGIN;

-- Disable triggers during migration for performance
SET session_replication_role = replica;

\echo 'Starting v4 to v6 migration...'
\echo ''
\echo 'IMPORTANT: This migration assumes:'
\echo '  1. v6 schemas (pyuser, pycore, pycommission, pycrm) already exist'
\echo '  2. v6 tables already exist (created by Alembic migrations)'
\echo '  3. v4 data is in the public schema'
\echo ''

\echo '01. Migrating users...'
\i 01_migrate_users.sql

\echo '02. Migrating customers...'
\i 02_migrate_customers.sql

\echo '03. Migrating factories...'
\i 03_migrate_factories.sql

\echo '04. Migrating product UOMs...'
\i 04_migrate_product_uoms.sql

\echo '05. Migrating product categories...'
\i 05_migrate_product_categories.sql

\echo '06. Migrating products...'
\i 06_migrate_products.sql

\echo '07. Migrating product CPNs...'
\i 07_migrate_product_cpns.sql

\echo '08. Migrating addresses...'
\i 08_migrate_addresses.sql

\echo '09. Migrating customer split rates...'
\i 09_migrate_customer_split_rates.sql

\echo '10. Migrating customer factory sales reps...'
\i 10_migrate_customer_factory_sales_reps.sql

\echo '11. Migrating orders...'
\i 11_migrate_orders.sql

\echo '12. Migrating order details...'
\i 12_migrate_order_details.sql

\echo '13. Migrating order split rates...'
\i 13_migrate_order_split_rates.sql

\echo '14. Migrating quotes...'
\i 14_migrate_quotes.sql

\echo '15. Migrating quote details...'
\i 15_migrate_quote_details.sql

\echo '16. Migrating quote split rates...'
\i 16_migrate_quote_split_rates.sql

\echo '17. Migrating invoices...'
\i 17_migrate_invoices.sql

\echo '18. Migrating invoice details...'
\i 18_migrate_invoice_details.sql

-- Re-enable triggers
SET session_replication_role = DEFAULT;

\echo ''
\echo 'Migration complete!'
\echo ''
\echo 'Post-migration checklist:'
\echo '  1. Verify row counts match between v4 and v6 tables'
\echo '  2. Spot check data integrity (especially UUID mappings)'
\echo '  3. Update sequences if needed for any auto-generated IDs'
\echo '  4. Run application tests against migrated data'

COMMIT;
