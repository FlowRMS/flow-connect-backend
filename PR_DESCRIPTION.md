## Description
Implements GraphQL backend modules for the warehouse settings feature, supporting the frontend settings page with shipping carriers, container types, and warehouse management functionality.

## Type of Change
- [ ] Bug fix
- [x] New feature
- [ ] Refactor
- [ ] Documentation
- [ ] Performance improvement
- [ ] Tests

## Changes Made
- Added **Shipping Carriers** module with full CRUD operations (6 endpoints)
- Added **Container Types** module with CRUD and drag-drop reordering (6 endpoints)
- Added **Warehouses** module with CRUD, members, settings, and structure management (9 endpoints)
- Created SQLAlchemy models for all entities using MappedAsDataclass pattern
- Added Alembic migration to extend `shipping_carriers` table with additional columns
- Implemented repository pattern with base repository inheritance
- Added Strawberry GraphQL types with automatic camelCase conversion

## Related Issues
Closes #

## How to Test
1. Start the backend: `uv run uvicorn app.main:app --reload --port 5555`
2. Open GraphQL playground: `http://localhost:5555/graphql`
3. Test queries with auth headers:
   ```json
   {"Authorization": "Bearer <token>", "X-Auth-Provider": "WORKOS"}
   ```
4. Example queries:
   ```graphql
   query { shippingCarriers { id name code isActive } }
   query { containerTypes { id name length width height order } }
   query { warehouses { id name status members { userId role } } }
   ```

## Checklist
- [x] Code follows project style guidelines
- [x] Self-reviewed my code
- [ ] Added/updated tests
- [ ] Documentation updated (if needed)
- [ ] No breaking changes (or documented below)

## Screenshots (if UI changes)
N/A - Backend API only

## Additional Notes
**Work in Progress:** 18/21 endpoints are fully working. Three warehouse mutations need fixes:

| Endpoint | Issue | Root Cause |
|----------|-------|------------|
| `updateWarehouse` | `created_at` null violation | SQLAlchemy MappedAsDataclass dirty tracking |
| `updateWarehouseSettings` | `warehouse_id` null | Strawberry input deserialization |
| `updateWarehouseStructure` | `warehouse_id` null | Strawberry input deserialization |

**New GraphQL Operations:**
- Shipping Carriers: `shippingCarriers`, `shippingCarrier(id)`, `shippingCarrierSearch(query)`, `createShippingCarrier`, `updateShippingCarrier`, `deleteShippingCarrier`
- Container Types: `containerTypes`, `containerType(id)`, `createContainerType`, `updateContainerType`, `reorderContainerTypes`, `deleteContainerType`
- Warehouses: `warehouses`, `warehouse(id)`, `warehouseMembers`, `warehouseSettings`, `warehouseStructure`, `createWarehouse`, `updateWarehouse`, `deleteWarehouse`, `updateWarehouseSettings`, `updateWarehouseStructure`
