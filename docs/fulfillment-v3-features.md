# Fulfillment V3 Features - Backend

## Overview

This release includes several backend enhancements to the fulfillment workflow, including document management, carrier type support, shipment request improvements, and status handling.

---

## 1. Fulfillment Documents

### Description
Backend support for attaching, viewing, and managing documents on fulfillment orders. Documents are stored in S3 and tracked in both the `pyfiles.files` table and the `pywarehouse.fulfillment_documents` table.

### Database Changes

#### New Table: `pywarehouse.fulfillment_documents`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| fulfillment_order_id | UUID | FK to fulfillment_orders |
| document_type | VARCHAR(50) | Type (BOL, PACKING_SLIP, etc.) |
| file_name | VARCHAR(255) | Original filename |
| file_url | TEXT | S3 presigned URL or path |
| file_id | UUID | FK to pyfiles.files (nullable) |
| file_size | INTEGER | File size in bytes |
| mime_type | VARCHAR(100) | MIME type |
| notes | TEXT | Optional notes |
| uploaded_at | TIMESTAMP | Upload timestamp |
| created_at | TIMESTAMP | Record creation time |
| created_by_id | UUID | FK to pycore.users |

### New Files
- `alembic/versions/20260107_add_fulfillment_documents_table.py` - Migration
- `repositories/fulfillment_document_repository.py` - Data access layer
- `services/fulfillment_document_service.py` - Business logic
- `strawberry/fulfillment_input.py` - GraphQL input types
- `strawberry/fulfillment_response.py` - GraphQL response types
- `mutations/fulfillment_mutations.py` - GraphQL mutations (updated)

### GraphQL API

#### Mutations
- `uploadFulfillmentDocument(input: UploadFulfillmentDocumentInput!)` - Upload and attach document
- `deleteFulfillmentDocument(documentId: UUID!)` - Delete document and S3 file

---

## 2. Carrier Type Support

### Description
Adds carrier type field to shipping carriers for categorization (LTL, FTL, Parcel, Courier).

### Database Changes
- Migration: `20260106_add_carrier_type_to_shipping_carriers.py`
- New column: `carrier_type` (VARCHAR) on `pywarehouse.shipping_carriers`

### GraphQL API
- `ShippingCarrierResponse.carrierType` - New field
- `ShippingCarrierInput.carrierType` - New input field
- `shippingCarriersByType(carrierType: String!)` - New query

### Files Changed
- `shipping_carriers_queries.py`
- `shipping_carriers_repository.py`
- `shipping_carrier_service.py`
- `shipping_carrier_input.py`
- `shipping_carrier_response.py`

---

## 3. Fulfillment Status Enhancements

### Description
Improved status handling with timezone-aware timestamps and new COMMUNICATED status.

### New Mutations
- `markFulfillmentOrderCommunicated(fulfillmentOrderId: UUID!)` - Mark order as communicated to customer

### Timestamp Fixes
- All datetime fields now use UTC with proper timezone handling
- Affected services:
  - `fulfillment_packing_service.py`
  - `fulfillment_picking_service.py`
  - `fulfillment_shipping_service.py`
  - `fulfillment_order_service.py`

---

## 4. Shipment Request Improvements

### Description
Enhanced shipment request handling with better repository queries and service logic.

### Files Changed
- `shipment_request_repository.py` - Improved query methods
- `shipment_request_service.py` - Enhanced business logic

---

## 5. Freight Class Support

### Description
Adds freight class field to shipping carriers for LTL rating.

### Database Changes
- Migration: `20260107_add_freight_class_to_shipping_carriers.py`
- New column: `freight_class` on `pywarehouse.shipping_carriers`

---

## Test Data Scripts

New SQL scripts for testing fulfillment workflows:
- `scripts/seed_picking_test_data.sql` - Seed data for picking tests
- `scripts/seed_shipping_test_data.sql` - Seed data for shipping tests
