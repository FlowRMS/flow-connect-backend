# Fulfillment V3 Testing Plan

**Date Created**: 2026-01-05
**Feature Branch**: `feat/fulfillment-v3` (frontend), `feat/fulfillment-v2` (backend)

---

## Work Division Overview

This plan divides testing between two developers to avoid conflicts and ensure comprehensive coverage.

| Tab/Status | Complexity | Owner | Key Feature |
|------------|------------|-------|-------------|
| **PENDING** | Medium | Dev B | Release + Backorder Notice |
| **RELEASED** | Low | Dev B | Start picking |
| **PICKING** | High | Dev A | Inventory + Shortage Detection |
| **BACKORDER_REVIEW** | High | Dev A | Manager review of shortages |
| **PACKING** | Medium | Dev B | Pack items |
| **SHIPPED** | Medium | Dev A | Carrier + tracking |
| **DELIVERED** | Low | Dev B | Final state |

---

## Dev A Scope - Inventory, Shortage & Shipping

Focus: **Real data integration, inventory accuracy, shortage detection, shipping**

```
┌─────────────────────────────────────────────────────────────────────┐
│  DEV A RESPONSIBILITIES                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. PICKING Tab                                                     │
│     ✅ Real inventory locations display                             │
│     ✅ Picking allocation logic                                     │
│     ✅ Split picks (multiple locations)                             │
│     ⚠️  Shortage detection & alert banner                          │
│     ⚠️  "Report Backorder" button functionality                    │
│                                                                     │
│  2. BACKORDER_REVIEW Status                                         │
│     ⚠️  Manager sees reported shortage                              │
│     ⚠️  Review and approve/adjust quantities                       │
│                                                                     │
│  3. SHIPPING Tab                                                    │
│     - Carrier selection                                             │
│     - Tracking number entry                                         │
│     - Ship confirmation modal                                       │
│     - Email notification (if enabled)                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Dev A Test Cases

| # | Tab | Test Case | Steps | Expected Result |
|---|-----|-----------|-------|-----------------|
| A1 | PICKING | Inventory shows real locations | 1. Open fulfillment in PICKING status<br>2. Expand line item | Shows actual warehouse locations (A-01-01, etc.) |
| A2 | PICKING | Split pick allocation | 1. Item needs 25 units<br>2. Location A has 15, Location B has 20 | Shows: pick 15 from A, pick 10 from B |
| A3 | PICKING | Shortage detection | 1. Order needs 30 units<br>2. Only 25 available in inventory | Red alert banner: "X units short across Y locations" |
| A4 | PICKING | Report Backorder button | 1. Shortage detected<br>2. Click "Report Backorder" | Status changes to BACKORDER_REVIEW |
| A5 | BACKORDER_REVIEW | Manager review UI | 1. Open order in BACKORDER_REVIEW status | Shows shortage details, hold reason, review options |
| A6 | PICKING | Complete picking (no shortage) | 1. Mark all items as picked<br>2. Click "Complete Picking" | Status changes to PACKING |
| A7 | SHIPPED | Enter tracking number | 1. Order in SHIPPED status<br>2. Enter tracking number | Saves and displays tracking info |
| A8 | SHIPPED | Ship confirmation modal | 1. Click "Mark as Shipped"<br>2. Select carrier, enter tracking | Modal opens, submits, status updates |

### Dev A Files (Don't modify these if you're Dev B)

| File | Purpose |
|------|---------|
| `components/warehouse/fulfillment-detail/PickingInterface.tsx` | Picking UI with shortage detection |
| `components/warehouse/api/inventoryApi.ts` | Inventory API functions |
| `components/warehouse/api/useInventoryApi.ts` | Inventory React Query hooks |
| `components/warehouse/fulfillment-detail/modals/ShipmentConfirmationModal.tsx` | Shipping modal |

---

## Dev B Scope - Status Transitions & Backorder Resolution

Focus: **Status changes, UI components, backorder resolution options**

```
┌─────────────────────────────────────────────────────────────────────┐
│  DEV B RESPONSIBILITIES                                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. PENDING Tab                                                     │
│     - View fulfillment details                                      │
│     ⚠️  BackorderNotice component display                          │
│     ⚠️  4 backorder action buttons:                                │
│         • Manufacturer Direct                                       │
│         • Request Inventory                                         │
│         • Split Order                                               │
│         • Cancel Backorder                                          │
│                                                                     │
│  2. RELEASED Tab                                                    │
│     - Start picking action                                          │
│     - Priority display                                              │
│                                                                     │
│  3. PACKING Tab                                                     │
│     - Pack items UI                                                 │
│     - Box/package assignment                                        │
│     - Complete packing action                                       │
│                                                                     │
│  4. DELIVERED Tab                                                   │
│     - Final status display                                          │
│     - Completion timestamps                                         │
│                                                                     │
│  5. Fulfillment List Page                                           │
│     - Filters by status                                             │
│     - Warehouse selector                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Dev B Test Cases

| # | Tab | Test Case | Steps | Expected Result |
|---|-----|-----------|-------|-----------------|
| B1 | LIST | Filter by status | 1. Go to /warehouse/fulfillment<br>2. Click each status filter | Shows only matching orders |
| B2 | LIST | Warehouse selector | 1. Change selected warehouse in header | List updates to show that warehouse's orders |
| B3 | PENDING | BackorderNotice displays | 1. Open PENDING fulfillment<br>2. Has items with backorderQty > 0 | Yellow alert box with backorder details |
| B4 | PENDING | Manufacturer Direct action | 1. Click "Manufacturer Direct" button | Opens modal for direct ship request |
| B5 | PENDING | Request Inventory action | 1. Click "Request Inventory" button | Opens shipment request workflow |
| B6 | PENDING | Split Order action | 1. Click "Split Order" button | Opens split order workflow |
| B7 | PENDING | Cancel Backorder action | 1. Click "Cancel Backorder" button | Opens cancel modal, updates quantities |
| B8 | PENDING | Release to warehouse | 1. No backorders<br>2. Click "Release to Warehouse" | Status changes to RELEASED |
| B9 | RELEASED | Start picking | 1. Click "Start Picking" | Status changes to PICKING |
| B10 | PACKING | Pack items | 1. Enter packed quantities per line item | Saves packed qty |
| B11 | PACKING | Complete packing | 1. All items packed<br>2. Click "Complete Packing" | Status changes to SHIPPED |
| B12 | DELIVERED | View completion | 1. Open DELIVERED fulfillment | Shows all timestamps, tracking info |

### Dev B Files (Don't modify these if you're Dev A)

| File | Purpose |
|------|---------|
| `components/warehouse/fulfillment-detail/BackorderNotice.tsx` | Backorder alert component |
| `components/warehouse/fulfillment-detail/modals/CancelBackorderModal.tsx` | Cancel backorder modal |
| `components/warehouse/fulfillment-detail/PackingInterface.tsx` | Packing UI |
| `components/warehouse/FulfillmentList.tsx` | List page |
| `components/warehouse/FulfillmentOrderDetail.tsx` | PENDING/RELEASED view |

---

## Backorder/Shortage Flow Diagram

Both devs need to understand this flow:

```
                                    ┌─────────────────┐
                                    │  INVENTORY      │
                                    │  INSUFFICIENT   │
                                    └────────┬────────┘
                                             │
                    ┌────────────────────────┴────────────────────────┐
                    │                                                 │
                    ▼                                                 ▼
        ┌───────────────────────┐                       ┌───────────────────────┐
        │  DETECTED AT CREATION │                       │  DETECTED AT PICKING  │
        │  (Before Release)     │                       │  (Worker Finds Less)  │
        │  backorderQty > 0     │                       │  pickedQty < expected │
        └───────────┬───────────┘                       └───────────┬───────────┘
                    │                                               │
                    ▼                                               ▼
        ┌───────────────────────┐                       ┌───────────────────────┐
        │  BackorderNotice      │                       │  Shortage Alert       │
        │  Shows on PENDING     │                       │  in PickingInterface  │
        │                       │                       │                       │
        │  DEV B Tests:         │                       │  DEV A Tests:         │
        │  • Manufacturer Direct│                       │  • Red banner shows   │
        │  • Request Inventory  │                       │  • "X units short"    │
        │  • Split Order        │                       │  • Report Backorder   │
        │  • Cancel Backorder   │                       │    button works       │
        └───────────────────────┘                       └───────────┬───────────┘
                                                                    │
                                                                    ▼
                                                        ┌───────────────────────┐
                                                        │  BACKORDER_REVIEW     │
                                                        │  Status               │
                                                        │                       │
                                                        │  DEV A Tests:         │
                                                        │  Manager review UI    │
                                                        └───────────────────────┘
```

---

## Test Data Setup

### Option 1: Use Existing Seed Script

```bash
# From flow-py-backend directory
psql -h <host> -U <user> -d <database> -f scripts/seed_fulfillment_test_data.sql
```

This creates:
- Warehouse: `TEST-WH-001`
- Products: `TEST-PROD-001`, `TEST-PROD-002`, `TEST-PROD-003`
- Fulfillment order in RELEASED status
- Test scenarios:
  - Product 1: Pick 25 from 2 locations (split pick)
  - Product 2: Pick 10 from 1 location (simple pick)
  - Product 3: 30 ordered but only 25 available (shortage test)

### Option 2: Create Separate Orders for Each Dev

```sql
-- DEV A Test Order (for picking/shortage tests)
-- Use fulfillment ID: <uuid-for-dev-a>

-- DEV B Test Order (for status transition tests)
-- Use fulfillment ID: <uuid-for-dev-b>
```

### Reset Fulfillment Status (for re-testing)

```sql
-- Reset to PENDING
UPDATE pywarehouse.fulfillment_orders
SET status = 'PENDING',
    released_at = NULL,
    picked_at = NULL,
    packed_at = NULL,
    shipped_at = NULL
WHERE id = '<fulfillment-id>';

-- Reset to RELEASED
UPDATE pywarehouse.fulfillment_orders
SET status = 'RELEASED',
    released_at = NOW(),
    picked_at = NULL,
    packed_at = NULL,
    shipped_at = NULL
WHERE id = '<fulfillment-id>';

-- Reset to PICKING
UPDATE pywarehouse.fulfillment_orders
SET status = 'PICKING',
    released_at = NOW(),
    picked_at = NULL,
    packed_at = NULL,
    shipped_at = NULL
WHERE id = '<fulfillment-id>';
```

---

## Communication Checkpoints

| Scenario | Who Notifies | Message |
|----------|--------------|---------|
| BackorderNotice UI working | Dev B → Dev A | "Backorder notice renders with all 4 action buttons" |
| Shortage detection working | Dev A → Dev B | "Picking shortage alert triggers correctly" |
| BACKORDER_REVIEW status works | Dev A → Dev B | "Report Backorder changes status correctly" |
| Cancel backorder works | Dev B → Dev A | "Cancel updates lineItem quantities in DB" |
| Status transition blocked | Either | "Found issue: [description]" |
| Ready to test handoff | Either | "PICKING complete, order ready for PACKING test" |

---

## Bug Reporting Template

When you find an issue in the other dev's area:

```markdown
**Component**: [File name]
**Status/Tab**: [PENDING/PICKING/etc]
**Issue**: [Brief description]
**Steps to Reproduce**:
1.
2.
3.
**Expected**:
**Actual**:
**Screenshot**: [if applicable]
```

---

## Checklist Summary

### Dev A Checklist
- [ ] A1: Inventory shows real locations
- [ ] A2: Split pick allocation works
- [ ] A3: Shortage detection shows alert
- [ ] A4: Report Backorder changes status
- [ ] A5: BACKORDER_REVIEW UI displays correctly
- [ ] A6: Complete picking transitions to PACKING
- [ ] A7: Tracking number saves
- [ ] A8: Ship confirmation modal works

### Dev B Checklist
- [ ] B1: Status filters work
- [ ] B2: Warehouse selector updates list
- [ ] B3: BackorderNotice displays
- [ ] B4: Manufacturer Direct action works
- [ ] B5: Request Inventory action works
- [ ] B6: Split Order action works
- [ ] B7: Cancel Backorder action works
- [ ] B8: Release to warehouse works
- [ ] B9: Start picking works
- [ ] B10: Pack items saves quantities
- [ ] B11: Complete packing transitions to SHIPPED
- [ ] B12: Delivered view shows all info

---

## Related Documentation

- [Fulfillment V3 Implementation Guide](./fulfillment-v3-implementation.md)
- Seed script: `flow-py-backend/scripts/seed_fulfillment_test_data.sql`
