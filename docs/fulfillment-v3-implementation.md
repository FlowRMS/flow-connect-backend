# Fulfillment V3 Implementation Guide

**Date Created**: 2026-01-05
**Status**: In Progress
**Version**: 3.0

---

## Table of Contents

1. [Overview](#overview)
2. [Fulfillment Workflow](#fulfillment-workflow)
3. [Repository Structure](#repository-structure)
4. [Branch Strategy](#branch-strategy)
5. [Backend Implementation](#backend-implementation)
6. [Frontend Implementation](#frontend-implementation)
7. [Picking Allocation Logic](#picking-allocation-logic)
8. [GraphQL API Reference](#graphql-api-reference)
9. [Local Development Notes](#local-development-notes)
10. [Testing](#testing)
11. [TODO / Missing Implementation](#todo--missing-implementation)
12. [Next Steps](#next-steps)

---

## Overview

The Fulfillment V3 feature enables warehouse operations to process orders through a complete fulfillment workflow including picking, packing, and shipping. This implementation integrates real-time inventory data with the picking interface, allowing warehouse staff to see actual stock locations and quantities when fulfilling orders.

### Key Capabilities

- Real-time inventory lookup by product and warehouse
- Batch inventory queries for efficient picking operations
- Smart picking allocation from available inventory locations
- Integration between order line items and physical inventory locations

---

## Fulfillment Workflow

### End-to-End Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           FULFILLMENT LIFECYCLE                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐      ┌──────────────┐      ┌───────────────┐      ┌─────────────┐
  │  ORDER   │ ──▶  │  FULFILLMENT │ ──▶  │   WAREHOUSE   │ ──▶  │  CUSTOMER   │
  │ CREATION │      │   CREATION   │      │  PROCESSING   │      │  DELIVERY   │
  └──────────┘      └──────────────┘      └───────────────┘      └─────────────┘
       │                   │                     │                      │
       ▼                   ▼                     ▼                      ▼
   Order Page        Order Detail          Fulfillment UI          Tracking
   (CRM/Sales)       "Create Fulfillment"  Picking/Packing         Shipping
                     ❌ NOT CONNECTED      ✅ WORKING               ⏳ PARTIAL
```

### 1. Order Creation (Source of Fulfillment)

**Where it starts**: Orders are created in the CRM/Sales module

**Location**: `flow-crm/app/(app)/orders/` and `flow-crm/components/orders/`

**Key Files**:
- `flow-crm/app/(app)/orders/page.tsx` - Orders list page
- `flow-crm/app/(app)/orders/[orderId]/page.tsx` - Order detail page
- `flow-crm/components/orders/detail/` - Order detail components

**Order Data Model** (relevant fields for fulfillment):
```typescript
interface Order {
  id: string;
  orderNumber: string;
  status: OrderStatus;  // DRAFT, SUBMITTED, APPROVED, etc.
  lineItems: OrderLineItem[];
  shipToAddress: Address;
  customerId: string;
  customerName: string;
}

interface OrderLineItem {
  id: string;
  productId: string;
  sku: string;
  description: string;
  quantity: number;
  unitPrice: number;
}
```

### 2. Fulfillment Order Creation (❌ NOT CONNECTED)

**What should happen**: User clicks "Create Fulfillment" on Order Detail page

**Current State**: Button shows `alert('Fulfillment request - coming soon')`

**UI Flow**:
```
Order Detail Page
      │
      ▼
┌─────────────────────────────────────┐
│  [Create Fulfillment] Button        │  ◀── OrderDetailHeader.tsx
│  (in order actions dropdown)        │
└─────────────────────────────────────┘
      │
      ▼ (should open)
┌─────────────────────────────────────┐
│  FulfillmentRequestModal            │  ◀── EXISTS but not wired
│  - Select warehouse                 │
│  - Review line items                │
│  - Confirm quantities               │
└─────────────────────────────────────┘
      │
      ▼ (should call)
┌─────────────────────────────────────┐
│  createFulfillmentOrder mutation    │  ◀── API EXISTS
│  POST /graphql                      │
│  - orderId                          │
│  - warehouseId                      │
│  - lineItems[]                      │
│  - shipTo address                   │
└─────────────────────────────────────┘
      │
      ▼ (should create)
┌─────────────────────────────────────┐
│  FulfillmentOrder (status: PENDING) │  ◀── Database record
└─────────────────────────────────────┘
```

**Files Involved**:
| File | Purpose | Status |
|------|---------|--------|
| `components/orders/detail/components/header/OrderDetailHeader.tsx` | Contains "Create Fulfillment" button | ❌ Shows alert only |
| `components/orders/detail/components/modals/utility/FulfillmentRequestModal.tsx` | Modal UI for creating fulfillment | ✅ UI Complete |
| `components/warehouse/api/fulfillmentOrdersApi.ts` | API function `createFulfillmentOrder` | ✅ Ready |
| `components/warehouse/api/useFulfillmentOrdersApi.ts` | React Query hook `useCreateFulfillmentOrder` | ✅ Ready |

### 3. Fulfillment Order Status Lifecycle

```
┌──────────┐    ┌──────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌───────────┐
│ PENDING  │ ─▶ │ RELEASED │ ─▶ │ PICKING │ ─▶ │ PACKING │ ─▶ │ SHIPPED │ ─▶ │ DELIVERED │
└──────────┘    └──────────┘    └─────────┘    └─────────┘    └─────────┘    └───────────┘
     │               │               │              │              │               │
     ▼               ▼               ▼              ▼              ▼               ▼
  Created        Released        Worker         Worker        Carrier         Customer
  awaiting       to warehouse    picks items    packs box     in transit      received
  approval       floor           from locations and labels
```

**Status Definitions**:

| Status | Description | Who Acts | Next Action |
|--------|-------------|----------|-------------|
| `PENDING` | Created, awaiting release | Manager | Release to warehouse |
| `RELEASED` | Ready for picking | Warehouse Worker | Start picking |
| `PICKING` | Worker collecting items | Warehouse Worker | Complete picking |
| `PACKING` | Items being boxed | Warehouse Worker | Complete packing |
| `SHIPPED` | Handed to carrier | System/Carrier | Track delivery |
| `DELIVERED` | Customer received | N/A | Complete |

### 4. Warehouse Processing (✅ WORKING)

**Location**: `flow-crm/app/(app)/warehouse/` and `flow-crm/components/warehouse/`

#### Fulfillment List Page
**URL**: `/warehouse/fulfillment`
**File**: `flow-crm/app/(app)/warehouse/fulfillment/page.tsx`

Shows all fulfillment orders for the selected warehouse with status filters.

#### Fulfillment Detail Page
**URL**: `/warehouse/fulfillment/[id]`
**File**: `flow-crm/app/(app)/warehouse/fulfillment/[id]/page.tsx`

**Key Component**: `FulfillmentOrderDetailContent.tsx`

Shows fulfillment details and renders different interfaces based on status:

```typescript
// Simplified logic from FulfillmentOrderDetailContent.tsx
switch (fulfillmentOrder.status) {
  case 'PICKING':
    return <PickingInterface inventoryData={inventoryDataMap} />;
  case 'PACKING':
    return <PackingInterface />;
  case 'SHIPPED':
  case 'DELIVERED':
    return <ShippingInterface />;
  default:
    return <FulfillmentOrderDetail />;  // PENDING, RELEASED
}
```

#### Picking Interface (✅ CONNECTED TO REAL INVENTORY)

**File**: `components/warehouse/fulfillment-detail/PickingInterface.tsx`

**Data Flow**:
```
FulfillmentOrderDetailContent
      │
      │ useInventoriesByProducts(productIds, warehouseId)
      ▼
┌─────────────────────────────────────┐
│ GraphQL: inventoriesByProducts      │
│ Returns: Inventory[] with items     │
└─────────────────────────────────────┘
      │
      │ Map<productId, Inventory>
      ▼
┌─────────────────────────────────────┐
│ PickingInterface                    │
│ - Shows line items to pick          │
│ - Displays real inventory locations │
│ - calculatePickingAllocation()      │
└─────────────────────────────────────┘
```

### 5. Data Models

#### FulfillmentOrder (Database: `pywarehouse.fulfillment_orders`)

```typescript
interface FulfillmentOrder {
  id: string;                    // UUID
  orderNumber: string;           // "FO-2026-0001"
  orderId: string;               // Reference to source order
  warehouseId: string;           // Which warehouse fulfills this
  status: FulfillmentStatus;
  priority: Priority;            // LOW, NORMAL, HIGH, URGENT

  // Shipping info
  shipTo: ShipToAddress;
  carrier: string;
  trackingNumber: string;

  // Line items
  lineItems: FulfillmentLineItem[];

  // Timestamps
  createdAt: string;
  releasedAt: string;
  pickedAt: string;
  packedAt: string;
  shippedAt: string;
  deliveredAt: string;
}

interface FulfillmentLineItem {
  id: string;
  fulfillmentOrderId: string;
  productId: string;
  sku: string;
  description: string;
  orderedQuantity: number;       // From original order
  pickedQuantity: number;        // Actually picked
  packedQuantity: number;        // Actually packed
  status: LineItemStatus;
}
```

#### Inventory (Database: `pywarehouse.inventory`)

```typescript
interface Inventory {
  id: string;
  productId: string;
  warehouseId: string;
  totalQuantity: number;
  availableQuantity: number;     // Can be picked
  reservedQuantity: number;      // Reserved for orders
  pickingQuantity: number;       // Currently being picked
  items: InventoryItem[];        // Physical locations
}

interface InventoryItem {
  id: string;
  inventoryId: string;
  locationId: string;            // Bin/shelf location
  locationName: string;          // "A-01-02" (Aisle-Rack-Shelf)
  quantity: number;
  status: 'AVAILABLE' | 'RESERVED' | 'PICKING' | 'DAMAGED';
  lotNumber: string;
}
```

### 6. API Endpoints

#### Queries (Read)
| Query | Purpose | Used By |
|-------|---------|---------|
| `fulfillmentOrders(warehouseId)` | List all fulfillment orders | Fulfillment list page |
| `fulfillmentOrder(id)` | Get single order details | Fulfillment detail page |
| `inventoriesByProducts(productIds, warehouseId)` | Get inventory for picking | Picking interface |

#### Mutations (Write)
| Mutation | Purpose | Status |
|----------|---------|--------|
| `createFulfillmentOrder` | Create new fulfillment from order | ✅ Backend ready, ❌ Frontend not connected |
| `updateFulfillmentOrderStatus` | Change status (release, pick, pack, ship) | ✅ Working |
| `updateFulfillmentLineItem` | Update picked/packed quantities | ✅ Working |

---

## Repository Structure

The fulfillment feature spans three repositories:

| Repository | Technology Stack | Purpose |
|------------|------------------|---------|
| **flow-crm** | React, Next.js, TypeScript | Frontend application with fulfillment UI |
| **flow-py-backend** | Python, Strawberry GraphQL, SQLAlchemy | Backend API and business logic |
| **flowbot-commons** | Python, SQLAlchemy | Shared database models and utilities |

---

## Branch Strategy

### Branch Naming

| Repository | Branch Name | Based On |
|------------|-------------|----------|
| flow-crm | `feat/fulfillment-v3` | `staging-v6` |
| flow-py-backend | `feat/fulfillment-v2` | `staging-v6` |
| flowbot-commons | `feat/fulfillment-v2` | `staging-v6` |

### Branch Merge History

The backend and commons branches (`feat/fulfillment-v2`) include merges from:

1. **`feat/inventory`** - Inventory management features
2. **`feat/settings`** - Application settings features

```
staging-v6
    |
    +-- feat/inventory --------+
    |                          |
    +-- feat/settings ---------+
    |                          |
    +-- feat/fulfillment-v2 <--+ (backend/commons)
    |
    +-- feat/fulfillment-v3    (frontend)
```

---

## Backend Implementation

### Inventory Repository

**File**: `app/graphql/v2/core/inventory/repositories/inventory_repository.py`

#### New Methods

```python
async def find_by_product(
    self,
    product_id: UUID,
    warehouse_id: UUID | None = None,
) -> Inventory | None:
    """Get inventory record for a product, optionally filtered by warehouse."""

async def find_by_products(
    self,
    product_ids: list[UUID],
    warehouse_id: UUID,
) -> list[Inventory]:
    """Get inventory records for multiple products in a warehouse."""
```

### Inventory Service

**File**: `app/graphql/v2/core/inventory/services/inventory_service.py`

```python
async def get_by_product(self, product_id: UUID, warehouse_id: UUID | None = None) -> Inventory | None
async def get_by_products(self, product_ids: list[UUID], warehouse_id: UUID) -> list[Inventory]
```

### Inventory GraphQL Queries

**File**: `app/graphql/v2/core/inventory/queries/inventory_queries.py`

```graphql
# Get inventory for a single product
inventoryByProduct(productId: UUID!, warehouseId: UUID!): InventoryResponse

# Get inventory for multiple products (batch query for picking)
inventoriesByProducts(productIds: [UUID!]!, warehouseId: UUID!): [InventoryResponse!]!
```

---

## Frontend Implementation

### New Files Created

#### `components/warehouse/api/inventoryApi.ts`

Types and API functions for inventory operations:

```typescript
// Types
export type InventoryItemStatus = 'AVAILABLE' | 'RESERVED' | 'PICKING' | 'DAMAGED' | 'QUARANTINE';
export type OwnershipType = 'CONSIGNMENT' | 'OWNED' | 'THIRD_PARTY';
export type ABCClass = 'A' | 'B' | 'C';

export interface InventoryItem {
  id: string;
  inventoryId: string;
  locationId: string | null;
  locationName: string | null;
  quantity: number;
  lotNumber: string | null;
  status: InventoryItemStatus;
  receivedDate: string | null;
}

export interface Inventory {
  id: string;
  productId: string;
  warehouseId: string;
  totalQuantity: number;
  availableQuantity: number;
  reservedQuantity: number;
  pickingQuantity: number;
  ownershipType: OwnershipType;
  abcClass: ABCClass | null;
  items: InventoryItem[];
  product: InventoryProduct;
}

// API Functions
export async function fetchInventoriesByProducts(productIds: string[], warehouseId: string): Promise<Inventory[]>
export async function fetchInventoryByProduct(productId: string, warehouseId: string): Promise<Inventory | null>

// Picking Helper
export function calculatePickingAllocationFromInventory(inventory: Inventory, qtyNeeded: number): PickingAllocation[]
```

#### `components/warehouse/api/useInventoryApi.ts`

React Query hooks:

```typescript
export const inventoryKeys = {
  all: ['inventory'] as const,
  byProduct: (productId: string, warehouseId: string) => [...],
  byProducts: (productIds: string[], warehouseId: string) => [...],
  // ...
};

export function useInventoriesByProducts(productIds: string[], warehouseId: string, queryOptions?: { enabled?: boolean })
export function useInventoryByProduct(productId: string, warehouseId: string, queryOptions?: { enabled?: boolean })
```

### Modified Files

#### `components/warehouse/fulfillment-detail/PickingInterface.tsx`

- Added `inventoryData` prop to accept real inventory data
- Added `getAllocationsForLineItem()` helper that uses real inventory when available, falls back to mock data

```typescript
interface PickingInterfaceProps {
  // ... existing props
  inventoryData?: Map<string, Inventory>;
}
```

#### `components/warehouse/FulfillmentOrderDetailContent.tsx`

- Fetches inventory data using `useInventoriesByProducts` when in picking mode
- Creates a `Map<productId, Inventory>` for efficient lookup
- Passes inventory data to PickingInterface

---

## Picking Allocation Logic

The `calculatePickingAllocationFromInventory` function:

1. **Filters** inventory items to only AVAILABLE status with quantity > 0
2. **Sorts** by quantity descending (pick from largest stocks first for efficiency)
3. **Allocates** from each location until the requested quantity is fulfilled

```typescript
export function calculatePickingAllocationFromInventory(
  inventory: Inventory,
  qtyNeeded: number
): PickingAllocation[] {
  const allocations: PickingAllocation[] = [];
  let remaining = qtyNeeded;

  const availableItems = inventory.items
    .filter((item) => item.status === 'AVAILABLE' && item.quantity > 0)
    .sort((a, b) => b.quantity - a.quantity);

  for (const item of availableItems) {
    if (remaining <= 0) break;
    const pickFromHere = Math.min(item.quantity, remaining);
    if (pickFromHere > 0) {
      allocations.push({
        locationId: item.locationId || 'unassigned',
        locationName: item.locationName || 'Unassigned',
        locationType: 'PRIMARY',
        quantity: pickFromHere,
        inventoryItemId: item.id,
      });
      remaining -= pickFromHere;
    }
  }
  return allocations;
}
```

---

## GraphQL API Reference

### Queries

#### `inventoryByProduct`

```graphql
query InventoryByProduct($productId: UUID!, $warehouseId: UUID!) {
  inventoryByProduct(productId: $productId, warehouseId: $warehouseId) {
    id
    productId
    warehouseId
    totalQuantity
    availableQuantity
    reservedQuantity
    pickingQuantity
    items {
      id
      locationId
      locationName
      quantity
      status
    }
    product {
      id
      factoryPartNumber
      description
    }
  }
}
```

#### `inventoriesByProducts`

```graphql
query InventoriesByProducts($productIds: [UUID!]!, $warehouseId: UUID!) {
  inventoriesByProducts(productIds: $productIds, warehouseId: $warehouseId) {
    id
    productId
    # ... same fields as above
  }
}
```

---

## Local Development Notes

### Files with Local Modifications (NOT committed)

These files have local modifications for development that should **NOT** be committed:

| File | Purpose |
|------|---------|
| `alembic/env.py` | Loads local `.env` file for database connection |
| `pyproject.toml` | Uses local editable path for flowbot-commons: `path = "../flowbot-commons"` |
| `uv.lock` | Reflects local pyproject changes |

### Running Locally

1. Backend uses local commons: `flow-py-commons = { path = "../flowbot-commons", editable = true }`
2. Alembic loads from `.env.staging` by default

---

## Testing

### Seed Data Script

A SQL script is available to create test data:

**File**: `scripts/seed_fulfillment_test_data.sql`

Creates:
- 1 Warehouse (`TEST-WH-001`) with hierarchical locations
- 3 Products (`TEST-PROD-001`, `TEST-PROD-002`, `TEST-PROD-003`)
- Inventory with items at specific locations
- 1 Order with 3 line items
- 1 Fulfillment Order in RELEASED status

**Test Scenarios:**
- Product 1: Pick 25 from 2 locations (split pick)
- Product 2: Pick 10 from 1 location (simple pick)
- Product 3: 30 ordered but only 25 available (backorder test)

```bash
psql -h <host> -U <user> -d <database> -f scripts/seed_fulfillment_test_data.sql
```

---

## TODO / Missing Implementation

### Critical: Fulfillment Order Creation NOT Connected

The flow from Order → Fulfillment Order is **NOT fully implemented**. The UI components exist but are not wired to the API.

#### What EXISTS:

| Component | Location | Status |
|-----------|----------|--------|
| FulfillmentRequestModal UI | `flow-crm/components/orders/detail/components/modals/utility/FulfillmentRequestModal.tsx` | ✅ UI Complete |
| createFulfillmentOrder API | `flow-crm/components/warehouse/api/fulfillmentOrdersApi.ts` | ✅ API Ready |
| useCreateFulfillmentOrder hook | `flow-crm/components/warehouse/api/useFulfillmentOrdersApi.ts` | ✅ Hook Ready |
| Backend mutation | `flow-py-backend` GraphQL | ✅ Backend Ready |

#### What is MISSING:

**File**: `flow-crm/components/orders/detail/components/header/OrderDetailHeader.tsx`

```typescript
// CURRENT (NOT WORKING):
handleGenerateFulfillmentRequest = () => {
  alert('Fulfillment request - coming soon');
},
```

#### Required Implementation:

1. **Wire up the modal's onConfirm callback** to call `createFulfillmentOrder` mutation
2. **Map order line items** to fulfillment line items with correct data structure
3. **Select warehouse** - user needs to pick which warehouse will fulfill the order
4. **Handle success/error states** and navigate to the new fulfillment order
5. **Validate order status** - only allow fulfillment creation for appropriate order statuses

#### Suggested Implementation Steps:

```typescript
// In OrderDetailHeader.tsx or parent component:

const { mutate: createFulfillmentOrder } = useCreateFulfillmentOrder();

const handleGenerateFulfillmentRequest = async (selectedWarehouseId: string) => {
  const lineItems = order.lineItems.map(li => ({
    productId: li.productId,
    orderedQuantity: li.quantity,
    sku: li.sku,
    description: li.description,
  }));

  createFulfillmentOrder({
    orderId: order.id,
    warehouseId: selectedWarehouseId,
    lineItems,
    shipTo: {
      name: order.shipToAddress?.name,
      addressLine1: order.shipToAddress?.street,
      city: order.shipToAddress?.city,
      state: order.shipToAddress?.state,
      postalCode: order.shipToAddress?.postalCode,
      country: order.shipToAddress?.country,
    },
  }, {
    onSuccess: (newFulfillment) => {
      toast.success('Fulfillment order created');
      router.push(`/warehouse/fulfillment/${newFulfillment.id}`);
    },
    onError: (error) => {
      toast.error(`Failed to create fulfillment: ${error.message}`);
    }
  });
};
```

### Other Pending Items

| Feature | Status | Notes |
|---------|--------|-------|
| Picking confirmation API | 🔶 Needs Testing | Backend exists, frontend action needs verification |
| Packing workflow | 🔶 Partial | UI exists, needs integration testing |
| Shipping label generation | ❌ Not Started | Future feature |
| Batch fulfillment creation | ❌ Not Started | Create multiple fulfillments at once |

---

## Next Steps

1. **Implement fulfillment creation connection** (see TODO section above)
2. **Run seed script** to populate test data
3. **Test picking workflow** with real inventory data
4. **Verify allocation logic** displays correct locations
5. **Test shortage/backorder** reporting

---

## Change Log

| Date | Changes |
|------|---------|
| 2026-01-05 | Initial implementation - inventory API, picking integration |
