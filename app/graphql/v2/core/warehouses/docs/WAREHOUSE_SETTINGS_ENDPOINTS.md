# Warehouse Settings API Endpoints

This document lists all GraphQL endpoints created for the warehouse settings feature.

**Total Endpoints: 21**
- Container Types: 6 endpoints
- Shipping Carriers: 6 endpoints
- Warehouses: 9 endpoints

---

## Container Types (6 endpoints)

| # | Operation | Type | GraphQL | Status |
|---|-----------|------|---------|--------|
| 1 | List all | Query | `containerTypes` | ✅ PASSED |
| 2 | Get by ID | Query | `containerType(id: UUID)` | ✅ PASSED |
| 3 | Create | Mutation | `createContainerType(input: ContainerTypeInput)` | ✅ PASSED |
| 4 | Update | Mutation | `updateContainerType(id: UUID, input: ContainerTypeInput)` | ✅ PASSED |
| 5 | Delete | Mutation | `deleteContainerType(id: UUID)` | ✅ PASSED |
| 6 | Reorder | Mutation | `reorderContainerTypes(orderedIds: [UUID!]!)` | ✅ PASSED |

### ContainerTypeInput Fields
```graphql
input ContainerTypeInput {
  name: String!
  length: Float!
  width: Float!
  height: Float!
  weight: Float!
}
```

### ContainerTypeResponse Fields
```graphql
type ContainerTypeResponse {
  id: UUID!
  name: String!
  length: Float!
  width: Float!
  height: Float!
  weight: Float!
  position: Int!
  createdAt: DateTime!
}
```

---

## Shipping Carriers (6 endpoints)

| # | Operation | Type | GraphQL | Status |
|---|-----------|------|---------|--------|
| 1 | List all | Query | `shippingCarriers(activeOnly: Boolean)` | ✅ PASSED |
| 2 | Get by ID | Query | `shippingCarrier(id: UUID)` | ✅ PASSED |
| 3 | Search | Query | `shippingCarrierSearch(searchTerm: String!, limit: Int)` | ✅ PASSED |
| 4 | Create | Mutation | `createShippingCarrier(input: ShippingCarrierInput)` | ✅ PASSED |
| 5 | Update | Mutation | `updateShippingCarrier(id: UUID, input: ShippingCarrierInput)` | ✅ PASSED |
| 6 | Delete | Mutation | `deleteShippingCarrier(id: UUID)` | ✅ PASSED |

### ShippingCarrierInput Fields
```graphql
input ShippingCarrierInput {
  name: String!
  code: String
  accountNumber: String
  isActive: Boolean
  paymentTerms: String
  apiKey: String
  apiEndpoint: String
  trackingUrlTemplate: String
  serviceTypes: JSON          # JSONB in database
  defaultServiceType: String
  maxWeight: Float
  maxDimensions: String
  residentialSurcharge: Float
  fuelSurchargePercent: Float
  pickupSchedule: String
  pickupLocation: String
  remarks: String
  internalNotes: String
}
```

### ShippingCarrierResponse Fields
```graphql
type ShippingCarrierResponse {
  id: UUID!
  name: String!
  code: String
  accountNumber: String
  isActive: Boolean
  paymentTerms: String
  apiKey: String
  apiEndpoint: String
  trackingUrlTemplate: String
  serviceTypes: JSON
  defaultServiceType: String
  maxWeight: Float
  maxDimensions: String
  residentialSurcharge: Float
  fuelSurchargePercent: Float
  pickupSchedule: String
  pickupLocation: String
  remarks: String
  internalNotes: String
  createdAt: DateTime!
}
```

---

## Warehouses (9 endpoints)

| # | Operation | Type | GraphQL | Status |
|---|-----------|------|---------|--------|
| 1 | List all | Query | `warehouses` | ✅ PASSED |
| 2 | Get by ID | Query | `warehouse(id: UUID)` | ✅ PASSED |
| 3 | Create | Mutation | `createWarehouse(input: WarehouseInput)` | ✅ PASSED |
| 4 | Update | Mutation | `updateWarehouse(id: UUID, input: WarehouseInput)` | ✅ PASSED |
| 5 | Delete | Mutation | `deleteWarehouse(id: UUID)` | ✅ PASSED |
| 6 | Get members | Query | `warehouseMembers(warehouseId: UUID)` | ✅ PASSED |
| 7 | Assign worker | Mutation | `assignWorkerToWarehouse(warehouseId: UUID, userId: UUID, role: Int, roleName: String)` | ⏳ Ready |
| 8 | Update worker role | Mutation | `updateWorkerRole(warehouseId: UUID, userId: UUID, role: Int, roleName: String)` | ⏳ Ready |
| 9 | Remove worker | Mutation | `removeWorkerFromWarehouse(warehouseId: UUID, userId: UUID)` | ⏳ Ready |

### Additional Warehouse Sub-endpoints

| # | Operation | Type | GraphQL | Status |
|---|-----------|------|---------|--------|
| 10 | Get settings | Query | `warehouseSettings(warehouseId: UUID)` | ✅ PASSED |
| 11 | Update settings | Mutation | `updateWarehouseSettings(input: WarehouseSettingsInput)` | ⏳ Ready |
| 12 | Get structure | Query | `warehouseStructure(warehouseId: UUID)` | ✅ PASSED |
| 13 | Update structure | Mutation | `updateWarehouseStructure(warehouseId: UUID, levels: [WarehouseStructureLevelInput!]!)` | ⏳ Ready |

### WarehouseInput Fields
```graphql
input WarehouseInput {
  name: String!
  status: String
  latitude: Float
  longitude: Float
  description: String
  isActive: Boolean
}
```

### WarehouseSettingsInput Fields
```graphql
input WarehouseSettingsInput {
  warehouseId: UUID!
  autoGenerateCodes: Boolean
  requireLocation: Boolean
  showInPickLists: Boolean
  generateQrCodes: Boolean
}
```

### WarehouseStructureLevelInput Fields
```graphql
input WarehouseStructureLevelInput {
  code: Int!
  levelOrder: Int!
}
```

---

## Test Summary

| Category | Total | Passed | Ready | Failed |
|----------|-------|--------|-------|--------|
| Container Types | 6 | 6 | 0 | 0 |
| Shipping Carriers | 6 | 6 | 0 | 0 |
| Warehouses | 13 | 8 | 5 | 0 |
| **Total** | **25** | **20** | **5** | **0** |

### Status Legend
- ✅ **PASSED** - Endpoint tested and working
- ⏳ **Ready** - Endpoint implemented but requires user data to test (e.g., valid user ID)
- ❌ **FAILED** - Endpoint has issues

---

## Test Examples

### Container Types

```bash
# List all container types
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "{ containerTypes { id name length width height weight position } }"}'

# Get container type by ID
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "{ containerType(id: \"<uuid>\") { id name } }"}'

# Create container type
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { createContainerType(input: {name: \"Small Box\", length: 12.0, width: 10.0, height: 8.0, weight: 1.5}) { id name position } }"}'

# Update container type
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { updateContainerType(id: \"<uuid>\", input: {name: \"Updated Box\", length: 15.0, width: 12.0, height: 10.0, weight: 2.0}) { id name } }"}'

# Delete container type
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { deleteContainerType(id: \"<uuid>\") }"}'

# Reorder container types
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { reorderContainerTypes(orderedIds: [\"<uuid1>\", \"<uuid2>\", \"<uuid3>\"]) { id name position } }"}'
```

### Shipping Carriers

```bash
# List all shipping carriers
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "{ shippingCarriers { id name code isActive accountNumber } }"}'

# List active carriers only
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "{ shippingCarriers(activeOnly: true) { id name code } }"}'

# Search shipping carriers
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "{ shippingCarrierSearch(searchTerm: \"Fed\", limit: 10) { id name code } }"}'

# Get shipping carrier by ID
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "{ shippingCarrier(id: \"<uuid>\") { id name code apiEndpoint } }"}'

# Create shipping carrier
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { createShippingCarrier(input: {name: \"FedEx\", code: \"FEDX\", isActive: true}) { id name code } }"}'

# Update shipping carrier
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { updateShippingCarrier(id: \"<uuid>\", input: {name: \"FedEx Express\", isActive: true}) { id name } }"}'

# Delete shipping carrier
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { deleteShippingCarrier(id: \"<uuid>\") }"}'
```

### Warehouses

```bash
# List all warehouses
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "{ warehouses { id name status isActive latitude longitude } }"}'

# Get warehouse by ID
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "{ warehouse(id: \"<uuid>\") { id name description } }"}'

# Create warehouse
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { createWarehouse(input: {name: \"Main Warehouse\", status: \"active\", isActive: true}) { id name status } }"}'

# Update warehouse
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { updateWarehouse(id: \"<uuid>\", input: {name: \"Main Warehouse Updated\", description: \"Primary distribution center\"}) { id name } }"}'

# Delete warehouse
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { deleteWarehouse(id: \"<uuid>\") }"}'

# Get warehouse members
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "{ warehouseMembers(warehouseId: \"<uuid>\") { id userId role } }"}'

# Get warehouse settings
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "{ warehouseSettings(warehouseId: \"<uuid>\") { id autoGenerateCodes requireLocation showInPickLists generateQrCodes } }"}'

# Get warehouse structure
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "{ warehouseStructure(warehouseId: \"<uuid>\") { id code levelOrder } }"}'

# Assign worker to warehouse (requires valid user ID)
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { assignWorkerToWarehouse(warehouseId: \"<warehouse-uuid>\", userId: \"<user-uuid>\", role: 1) { id userId role } }"}'

# Update warehouse settings
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { updateWarehouseSettings(input: {warehouseId: \"<uuid>\", autoGenerateCodes: true, requireLocation: true}) { id autoGenerateCodes } }"}'

# Update warehouse structure
curl -X POST http://127.0.0.1:8006/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-Auth-Provider: WORKOS" \
  -d '{"query": "mutation { updateWarehouseStructure(warehouseId: \"<uuid>\", levels: [{code: 1, levelOrder: 1}, {code: 2, levelOrder: 2}]) { id code levelOrder } }"}'
```

---

## Notes

1. **Worker Management Endpoints**: The `assignWorkerToWarehouse`, `updateWorkerRole`, and `removeWorkerFromWarehouse` endpoints require a valid user UUID from the `pyuser.users` table. They were not fully tested because no test users were available in the database.

2. **Settings and Structure Mutations**: The `updateWarehouseSettings` and `updateWarehouseStructure` endpoints are implemented and ready but require creating warehouse data first.

3. **Authentication**: All endpoints require:
   - `Authorization: Bearer <token>` header
   - `X-Auth-Provider: WORKOS` header

4. **Database Schema**:
   - Container Types: `pycrm.container_types`
   - Shipping Carriers: `pycrm.shipping_carriers`
   - Warehouses: `pywarehouse.warehouses`
   - Warehouse Members: `pywarehouse.warehouse_members`
   - Warehouse Settings: `pywarehouse.warehouse_settings`
   - Warehouse Structure: `pywarehouse.warehouse_structure`
