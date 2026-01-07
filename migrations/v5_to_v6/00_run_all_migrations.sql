-- Master Migration Script: v5 to v6
-- This script runs all migrations in the correct order
--
-- IMPORTANT: Review each migration file before running!
-- Some migrations may need adjustments based on your specific data.
--
-- Run order:
-- 01. Users
-- 02. Customers
-- 03. Files & Folders
-- 04. Factories
-- 05. Product UOMs
-- 06. Product Categories
-- 07. Products
-- 08. Product CPNs
-- 09. Product Quantity Pricing
-- 10. Addresses
-- 11. Customer Split Rates
-- 12. Customer Factory Sales Reps
-- 13. Order Balances
-- 14. Orders
-- 15. Order Details
-- 16. Order Split Rates & Inside Reps
-- 17. Quote Balances
-- 18. Quote Lost Reasons
-- 19. Quotes
-- 20. Quote Details
-- 21. Quote Split Rates & Inside Reps
-- 22. Job Statuses
-- 23. Jobs
-- 24. Pre-Opportunity Balances
-- 25. Pre-Opportunities
-- 26. Pre-Opportunity Details

-- Schema mapping summary:
-- v5                          -> v6
-- user.users                  -> pyuser.users
-- core.customers              -> pycore.customers
-- core.factories              -> pycore.factories
-- core.products               -> pycore.products
-- core.product_uoms           -> pycore.product_uoms
-- core.product_categories     -> pycore.product_categories
-- core.product_cpns           -> pycore.product_cpns
-- core.product_quantity_pricing -> pycore.product_quantity_pricing
-- core.addresses              -> pycore.addresses
-- core.customer_split_rates   -> pycore.customer_split_rates
-- core.sales_rep_selections   -> pycore.customer_factory_sales_reps
-- commission.order_balances   -> pycommission.order_balances
-- commission.orders           -> pycommission.orders
-- commission.order_details    -> pycommission.order_details
-- commission.order_split_rates -> pycommission.order_split_rates
-- crm.quote_balances          -> pycrm.quote_balances
-- crm.quote_lost_reasons      -> pycrm.quote_lost_reasons
-- crm.quotes                  -> pycrm.quotes
-- crm.quote_details           -> pycrm.quote_details
-- crm.quote_split_rates       -> pycrm.quote_split_rates
-- crm.jobs                    -> pycrm.jobs
-- crm.pre_opportunity_balances -> pycrm.pre_opportunity_balances
-- crm.pre_opportunities       -> pycrm.pre_opportunities
-- crm.pre_opportunity_details -> pycrm.pre_opportunity_details
-- files.files                 -> pyfiles.files
-- files.folders               -> pyfiles.folders

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

\echo 'Starting v5 to v6 migration...'

\echo '01. Migrating users...'
\i 01_migrate_users.sql

\echo '02. Migrating customers...'
\i 02_migrate_customers.sql

\echo '03. Migrating files and folders...'
\i 03_migrate_files.sql

\echo '04. Migrating factories...'
\i 04_migrate_factories.sql

\echo '05. Migrating product UOMs...'
\i 05_migrate_product_uoms.sql

\echo '06. Migrating product categories...'
\i 06_migrate_product_categories.sql

\echo '07. Migrating products...'
\i 07_migrate_products.sql

\echo '08. Migrating product CPNs...'
\i 08_migrate_product_cpns.sql

\echo '09. Migrating product quantity pricing...'
\i 09_migrate_product_quantity_pricing.sql

\echo '10. Migrating addresses...'
\i 10_migrate_addresses.sql

\echo '11. Migrating customer split rates...'
\i 11_migrate_customer_split_rates.sql

\echo '12. Migrating customer factory sales reps...'
\i 12_migrate_customer_factory_sales_reps.sql

\echo '13. Migrating order balances...'
\i 13_migrate_order_balances.sql

\echo '14. Migrating orders...'
\i 14_migrate_orders.sql

\echo '15. Migrating order details...'
\i 15_migrate_order_details.sql

\echo '16. Migrating order split rates...'
\i 16_migrate_order_split_rates.sql

\echo '17. Migrating quote balances...'
\i 17_migrate_quote_balances.sql

\echo '18. Migrating quote lost reasons...'
\i 18_migrate_quote_lost_reasons.sql

\echo '19. Migrating quotes...'
\i 19_migrate_quotes.sql

\echo '20. Migrating quote details...'
\i 20_migrate_quote_details.sql

\echo '21. Migrating quote split rates...'
\i 21_migrate_quote_split_rates.sql

\echo '22. Migrating job statuses...'
\i 22_migrate_job_statuses.sql

\echo '23. Migrating jobs...'
\i 23_migrate_jobs.sql

\echo '24. Migrating pre-opportunity balances...'
\i 24_migrate_pre_opportunity_balances.sql

\echo '25. Migrating pre-opportunities...'
\i 25_migrate_pre_opportunities.sql

\echo '26. Migrating pre-opportunity details...'
\i 26_migrate_pre_opportunity_details.sql

-- Re-enable triggers
SET session_replication_role = DEFAULT;

\echo 'Migration complete!'

COMMIT;
