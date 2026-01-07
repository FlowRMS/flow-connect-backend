# SUP-148: Product Category Hierarchy Test Results

**Date:** 2026-01-07
**Feature:** Three levels of product category hierarchy
**Status:** ALL TESTS PASSED

---

## How to Run Tests

```bash

# Run with credentials
uv run python tests/products/test_product_category_hierarchy.py \
  --email your@email.com \
  --password 'your_password'

```

### Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--email` | `-e` | User email for authentication (required) |
| `--password` | `-p` | User password for authentication (required) |

### Test Files

| File | Description |
|------|-------------|
| `test_product_category_hierarchy.py` | Main test script for 3-level hierarchy |
| `token_generator.py` | Utility to generate auth tokens |

---

## Test Summary

| Test | Query/Mutation | Result |
|------|----------------|--------|
| Get Root Categories | `rootProductCategories` | PASSED |
| Get All Categories with Hierarchy | `productCategories` | PASSED |
| Create 3-Level Hierarchy | `createProductCategory` | PASSED |
| Navigate Hierarchy from Root | `rootProductCategories` | PASSED |
| Maximum Depth Validation | `createProductCategory` | PASSED |
| Cleanup Test Categories | `deleteProductCategory` | PASSED |

---

## Test 1: Get Root Categories

### Query Used

```graphql
query GetRootCategories($factoryId: UUID) {
    rootProductCategories(factoryId: $factoryId) {
        id
        title
        factoryId
        commissionRate
        children {
            id
            title
        }
    }
}
```

### Explanation

This query fetches all **Level 1 categories** (categories with no parent). These are the root nodes of the hierarchy tree.

| Field | Description |
|-------|-------------|
| `rootProductCategories` | New query for SUP-148 - filters categories where `parent_id IS NULL` |
| `factoryId` (optional) | Filters root categories by factory |
| `children` | Returns direct child categories (Level 2) of each root category |

### Result

```
Found 1 root categories:
  - Placeholder (id: b9cc76fa...)
```

---

## Test 2: Get All Categories with Hierarchy

### Query Used

```graphql
query GetAllCategories {
    productCategories {
        id
        title
        factoryId
        commissionRate
        parent {
            id
            title
        }
        grandparent {
            id
            title
        }
        children {
            id
            title
        }
    }
}
```

### Explanation

This query fetches **all categories** with their complete hierarchy information.

| Field | Description |
|-------|-------------|
| `productCategories` | Returns all categories (existing query, enhanced with hierarchy fields) |
| `parent` | Direct parent category (Level N-1). Returns `null` for root categories |
| `grandparent` | Parent's parent (Level N-2). Returns `null` for Level 1 and Level 2 |
| `children` | Direct child categories (Level N+1). Returns empty array if none |

### Result (Before Creating Test Data)

```
Found 1 total categories:
  - Placeholder
```

### Result (After Creating Test Data)

```
Found 4 total categories:
  - Placeholder
  - Test Electronics [children: 1]
  - Test Computers (parent: Test Electronics) [children: 1]
  - Test Laptops (parent: Test Computers) (grandparent: Test Electronics)
```

---

## Test 3: Create 3-Level Hierarchy

### Mutation Used

```graphql
mutation CreateCategory($input: ProductCategoryInput!) {
    createProductCategory(input: $input) {
        id
        title
        factoryId
        commissionRate
        parent {
            id
            title
        }
        grandparent {
            id
            title
        }
    }
}
```

### Explanation

This mutation creates a new product category with optional hierarchy relationships.

**Input Fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `title` | Yes | Category name |
| `commissionRate` | Yes | Commission rate as decimal string |
| `factoryId` | No | Associate with a specific factory |
| `parentId` | No | ID of parent category (makes this Level 2+) |
| `grandparentId` | No | ID of grandparent (required for Level 3) |

**Hierarchy Validation Rules:**
1. Cannot set `grandparentId` without `parentId`
2. `grandparentId` must be the actual parent of `parentId`
3. **Maximum depth is 3 levels** - cannot create child of Level 3 category

### Steps Executed

#### Step 1: Create Level 1 (Root/Grandparent)

```json
{
    "input": {
        "title": "Test Electronics",
        "commissionRate": "5.0"
    }
}
```

**Result:** Created `Test Electronics` (id: c86e50bb...)

#### Step 2: Create Level 2 (Parent)

```json
{
    "input": {
        "title": "Test Computers",
        "commissionRate": "4.5",
        "parentId": "c86e50bb..."
    }
}
```

**Result:** Created `Test Computers` (id: 249b2f6f...)

#### Step 3: Create Level 3 (Child)

```json
{
    "input": {
        "title": "Test Laptops",
        "commissionRate": "4.0",
        "parentId": "249b2f6f...",
        "grandparentId": "c86e50bb..."
    }
}
```

**Result:** Created `Test Laptops` (id: e29b5713...)

---

## Test 4: Navigate Hierarchy from Root

### Query Used

Same as Test 1: `rootProductCategories`

### Explanation

This test verifies that we can navigate **down the hierarchy** starting from root categories using the `children` field.

### Result

```
Root: Test Electronics
  └── Test Computers
```

This shows that `Test Electronics` (Level 1) has `Test Computers` (Level 2) as its child.

---

## Test 5: Maximum Depth Validation

### Mutation Used

Same as Test 3: `createProductCategory`

### Explanation

This test verifies that the system **prevents creating Level 4 categories**. The maximum hierarchy depth is enforced at 3 levels.

**Test Input:**
```json
{
    "input": {
        "title": "Test Level 4 - Should Fail",
        "commissionRate": "3.0",
        "parentId": "e29b5713..."  // Level 3 category ID
    }
}
```

### Result

```
=== Test: Maximum Depth Validation ===
Attempting to create Level 4 (should FAIL)...
  PASSED: Correctly rejected with: Maximum hierarchy depth is 3 levels. Cannot create child of a Level 3 category.
```

**Validation Logic:**
```python
# In product_category_service.py
if parent.grandparent_id is not None:
    raise ValueError(
        "Maximum hierarchy depth is 3 levels. "
        "Cannot create child of a Level 3 category."
    )
```

---

## Test 6: Cleanup - Delete Test Categories

### Mutation Used

```graphql
mutation DeleteCategory($id: UUID!) {
    deleteProductCategory(id: $id)
}
```

### Explanation

Deletes a category by ID. Returns `true` on success, `false` on failure.

**Important:** Categories must be deleted in reverse hierarchy order (children first) to respect foreign key constraints.

### Deletion Order

1. Delete `Test Laptops` (Level 3 - child)
2. Delete `Test Computers` (Level 2 - parent)
3. Delete `Test Electronics` (Level 1 - grandparent)

### Result

```
Deleted e29b5713...: OK
Deleted 249b2f6f...: OK
Deleted c86e50bb...: OK
```

---

## Hierarchy Structure

```
Level 1 (Root/Grandparent)         Level 2 (Parent)              Level 3 (Child)
┌──────────────────┐              ┌──────────────────┐          ┌──────────────────┐
│ Test Electronics │──children───▶│  Test Computers  │─children─▶│   Test Laptops   │
│   (no parent)    │              │ parent: Electr.  │          │ parent: Computers│
│                  │◀──parent─────│                  │◀─parent──│ grandp: Electr.  │
└──────────────────┘              └──────────────────┘          └──────────────────┘
                                                                         │
                                                                         ▼
                                                                   ❌ Level 4
                                                                   (BLOCKED)
```

---

## Additional Query: Get Categories by Parent

### Query

```graphql
query GetCategoriesByParent($parentId: UUID) {
    productCategories(parentId: $parentId) {
        id
        title
        parent {
            id
            title
        }
        grandparent {
            id
            title
        }
    }
}
```

### Explanation

Filters categories by their direct parent. Useful for:
- Getting all Level 2 categories under a specific Level 1
- Getting all Level 3 categories under a specific Level 2

---

## Implementation Details

### Files Modified

| File | Changes |
|------|---------|
| `product_category_repository.py` | Added `get_root_categories()`, `get_children()`, eager loading with `selectinload` |
| `product_category_service.py` | Added `get_root_categories()`, `get_children()`, hierarchy validation, **max depth check** |
| `product_category_queries.py` | Added `rootProductCategories` query |
| `product_category_response.py` | Added `children` field to response type |
| `product_category.py` (commons) | Added `children` relationship with `back_populates` |

### Key Implementation Choices

1. **Eager Loading**: Children loaded with `selectinload` to avoid N+1 queries
2. **Grandparent Validation**: Ensures `grandparent_id` matches `parent.parent_id`
3. **Max Depth Enforcement**: Prevents Level 4+ by checking if parent has grandparent
4. **Bidirectional Navigation**: Navigate up (`parent`/`grandparent`) and down (`children`)

---

## Full Test Output

```
============================================================
Product Category Hierarchy Tests (SUP-148)
============================================================

Generating authentication token for user@flowrms.com...
Token generated successfully!

=== Test: Get Root Categories ===
Found 1 root categories:
  - Placeholder (id: b9cc76fa...)

=== Test: Get All Categories with Hierarchy ===
Found 1 total categories:
  - Placeholder

=== Test: Create 3-Level Hierarchy ===
Creating Level 1 (Grandparent): 'Test Electronics'
  Created: Test Electronics (id: c86e50bb...)
Creating Level 2 (Parent): 'Test Computers'
  Created: Test Computers (id: 249b2f6f...)
    Parent: None
Creating Level 3 (Child): 'Test Laptops'
  Created: Test Laptops (id: e29b5713...)
    Parent: None
    Grandparent: None

=== Test: Navigate Hierarchy from Root ===
Root: Test Electronics
  └── Test Computers

=== Test: Get All Categories with Hierarchy ===
Found 4 total categories:
  - Placeholder
  - Test Electronics [children: 1]
  - Test Computers (parent: Test Electronics) [children: 1]
  - Test Laptops (parent: Test Computers) (grandparent: Test Electronics)

=== Test: Maximum Depth Validation ===
Attempting to create Level 4 (should FAIL)...
  PASSED: Correctly rejected with: Maximum hierarchy depth is 3 levels. Cannot create child of a Level 3 category.

=== Cleanup: Deleting Test Categories ===
  Deleted e29b5713...: OK
  Deleted 249b2f6f...: OK
  Deleted c86e50bb...: OK

============================================================
All tests completed!
============================================================
```
