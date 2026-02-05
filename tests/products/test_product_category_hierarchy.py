#!/usr/bin/env python3
import argparse
import asyncio
import sys
from pathlib import Path

import httpx

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.common.token_generator import generate_token

BASE_URL = "http://localhost:5555/graphql"


async def graphql_request(
    query: str,
    variables: dict | None = None,
    headers: dict | None = None,
) -> dict:
    """Execute a GraphQL request."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            BASE_URL,
            json={"query": query, "variables": variables or {}},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


# GraphQL Queries
GET_ROOT_CATEGORIES = """
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
"""

GET_ALL_CATEGORIES = """
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
"""

GET_CATEGORIES_BY_PARENT = """
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
"""

CREATE_CATEGORY = """
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
"""

DELETE_CATEGORY = """
mutation DeleteCategory($id: UUID!) {
    deleteProductCategory(id: $id)
}
"""


async def test_get_root_categories(headers: dict) -> None:
    """Test fetching root categories (Level 1 - no parent)."""
    print("\n=== Test: Get Root Categories ===")

    result = await graphql_request(GET_ROOT_CATEGORIES, headers=headers)

    if "errors" in result:
        print(f"ERROR: {result['errors']}")
        return

    categories = result["data"]["rootProductCategories"]
    print(f"Found {len(categories)} root categories:")
    for cat in categories:
        print(f"  - {cat['title']} (id: {cat['id'][:8]}...)")
        if cat["children"]:
            print(f"    Children: {[c['title'] for c in cat['children']]}")


async def test_get_all_categories(headers: dict) -> None:
    """Test fetching all categories with hierarchy info."""
    print("\n=== Test: Get All Categories with Hierarchy ===")

    result = await graphql_request(GET_ALL_CATEGORIES, headers=headers)

    if "errors" in result:
        print(f"ERROR: {result['errors']}")
        return

    categories = result["data"]["productCategories"]
    print(f"Found {len(categories)} total categories:")
    for cat in categories:
        parent_info = f" (parent: {cat['parent']['title']})" if cat["parent"] else ""
        grandparent_info = (
            f" (grandparent: {cat['grandparent']['title']})"
            if cat["grandparent"]
            else ""
        )
        children_info = (
            f" [children: {len(cat['children'])}]" if cat["children"] else ""
        )
        print(f"  - {cat['title']}{parent_info}{grandparent_info}{children_info}")


async def test_create_hierarchy(headers: dict) -> list[str]:
    """Test creating a 3-level hierarchy."""
    print("\n=== Test: Create 3-Level Hierarchy ===")

    created_ids = []

    # Level 1: Create grandparent (root category)
    print("Creating Level 1 (Grandparent): 'Test Electronics'")
    result = await graphql_request(
        CREATE_CATEGORY,
        variables={
            "input": {
                "title": "Test Electronics",
                "commissionRate": "5.0",
            }
        },
        headers=headers,
    )

    if "errors" in result:
        print(f"ERROR creating grandparent: {result['errors']}")
        return created_ids

    grandparent = result["data"]["createProductCategory"]
    grandparent_id = grandparent["id"]
    created_ids.append(grandparent_id)
    print(f"  Created: {grandparent['title']} (id: {grandparent_id[:8]}...)")

    # Level 2: Create parent
    print("Creating Level 2 (Parent): 'Test Computers'")
    result = await graphql_request(
        CREATE_CATEGORY,
        variables={
            "input": {
                "title": "Test Computers",
                "commissionRate": "4.5",
                "parentId": grandparent_id,
            }
        },
        headers=headers,
    )

    if "errors" in result:
        print(f"ERROR creating parent: {result['errors']}")
        return created_ids

    parent = result["data"]["createProductCategory"]
    parent_id = parent["id"]
    created_ids.append(parent_id)
    print(f"  Created: {parent['title']} (id: {parent_id[:8]}...)")
    print(f"    Parent: {parent['parent']['title'] if parent['parent'] else 'None'}")

    # Level 3: Create child
    print("Creating Level 3 (Child): 'Test Laptops'")
    result = await graphql_request(
        CREATE_CATEGORY,
        variables={
            "input": {
                "title": "Test Laptops",
                "commissionRate": "4.0",
                "parentId": parent_id,
                "grandparentId": grandparent_id,
            }
        },
        headers=headers,
    )

    if "errors" in result:
        print(f"ERROR creating child: {result['errors']}")
        return created_ids

    child = result["data"]["createProductCategory"]
    child_id = child["id"]
    created_ids.append(child_id)
    print(f"  Created: {child['title']} (id: {child_id[:8]}...)")
    print(f"    Parent: {child['parent']['title'] if child['parent'] else 'None'}")
    print(
        f"    Grandparent: {child['grandparent']['title'] if child['grandparent'] else 'None'}"
    )

    return created_ids


async def test_hierarchy_navigation(headers: dict, grandparent_id: str) -> None:
    """Test navigating the hierarchy using children field."""
    print("\n=== Test: Navigate Hierarchy from Root ===")

    result = await graphql_request(GET_ROOT_CATEGORIES, headers=headers)

    if "errors" in result:
        print(f"ERROR: {result['errors']}")
        return

    # Find our test grandparent
    root_cats = result["data"]["rootProductCategories"]
    test_root = next((c for c in root_cats if c["id"] == grandparent_id), None)

    if test_root:
        print(f"Root: {test_root['title']}")
        if test_root["children"]:
            for child in test_root["children"]:
                print(f"  └── {child['title']}")


async def test_max_depth_validation(headers: dict, level3_id: str) -> bool:
    """Test that Level 4 creation is blocked (max depth = 3)."""
    print("\n=== Test: Maximum Depth Validation ===")
    print("Attempting to create Level 4 (should FAIL)...")

    result = await graphql_request(
        CREATE_CATEGORY,
        variables={
            "input": {
                "title": "Test Level 4 - Should Fail",
                "commissionRate": "3.0",
                "parentId": level3_id,
            }
        },
        headers=headers,
    )

    if "errors" in result:
        error_msg = result["errors"][0]["message"]
        if "Maximum hierarchy depth" in error_msg or "3 levels" in error_msg:
            print(f"  PASSED: Correctly rejected with: {error_msg}")
            return True
        else:
            print(f"  FAILED: Rejected but wrong error: {error_msg}")
            return False
    else:
        # If it succeeded, we need to delete it and report failure
        created_id = result["data"]["createProductCategory"]["id"]
        print(f"  FAILED: Level 4 was created (id: {created_id[:8]}...)")
        print("  Cleaning up invalid Level 4 category...")
        await graphql_request(
            DELETE_CATEGORY,
            variables={"id": created_id},
            headers=headers,
        )
        return False


async def cleanup_test_categories(headers: dict, category_ids: list[str]) -> None:
    """Delete test categories (in reverse order to respect FK constraints)."""
    print("\n=== Cleanup: Deleting Test Categories ===")

    # Delete in reverse order (children first)
    for cat_id in reversed(category_ids):
        result = await graphql_request(
            DELETE_CATEGORY,
            variables={"id": cat_id},
            headers=headers,
        )

        if "errors" in result:
            print(f"ERROR deleting {cat_id[:8]}...: {result['errors']}")
        else:
            success = result["data"]["deleteProductCategory"]
            print(f"  Deleted {cat_id[:8]}...: {'OK' if success else 'FAILED'}")


async def run_tests(email: str, password: str, org_id: str | None = None):
    """Run all tests."""
    print("=" * 60)
    print("Product Category Hierarchy Tests (SUP-148)")
    print("=" * 60)

    # Generate authentication token
    print(f"\nGenerating authentication token for {email}...")
    try:
        headers = await generate_token(
            email=email, password=password, organization_id=org_id
        )
        print("Token generated successfully!")
    except Exception as e:
        print(f"Failed to generate token: {e}")
        return

    # Run tests
    try:
        # Test 1: Get existing root categories
        await test_get_root_categories(headers)

        # Test 2: Get all categories with hierarchy
        await test_get_all_categories(headers)

        # Test 3: Create a 3-level hierarchy
        created_ids = await test_create_hierarchy(headers)

        if created_ids and len(created_ids) == 3:
            # Test 4: Navigate hierarchy
            await test_hierarchy_navigation(headers, created_ids[0])

            # Test 5: Verify all categories again
            await test_get_all_categories(headers)

            # Test 6: Verify max depth validation (Level 4 should be blocked)
            level3_id = created_ids[2]  # The third category is Level 3
            await test_max_depth_validation(headers, level3_id)

            # Cleanup
            await cleanup_test_categories(headers, created_ids)

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except httpx.ConnectError:
        print("\nERROR: Could not connect to server at localhost:5555")
        print("Make sure the server is running: uv run ./start.py")
    except Exception as e:
        print(f"\nERROR: {e}")
        raise


def main():
    """Parse arguments and run tests."""
    parser = argparse.ArgumentParser(
        description="Test Product Category Hierarchy (SUP-148)"
    )
    parser.add_argument("--email", "-e", required=True, help="User email")
    parser.add_argument("--password", "-p", required=True, help="User password")
    parser.add_argument(
        "--org-id", "-o", help="Organization ID (required for multi-org users)"
    )

    args = parser.parse_args()

    asyncio.run(run_tests(email=args.email, password=args.password, org_id=args.org_id))


if __name__ == "__main__":
    main()
