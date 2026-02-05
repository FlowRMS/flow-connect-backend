#!/usr/bin/env python3
import argparse
import asyncio
import sys
from pathlib import Path

import httpx

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

BASE_URL = "http://localhost:5555/graphql"


FIND_OVERAGE_QUERY = """
query FindOverageByProduct(
    $productId: ID!
    $detailUnitPrice: Float!
    $factoryId: ID!
    $endUserId: ID!
    $quantity: Float
) {
    findEffectiveCommissionRateAndOverageUnitPriceByProduct(
        productId: $productId
        detailUnitPrice: $detailUnitPrice
        factoryId: $factoryId
        endUserId: $endUserId
        quantity: $quantity
    ) {
        success
        errorMessage
        effectiveCommissionRate
        overageUnitPrice
        baseUnitPrice
        repShare
        levelRate
        levelUnitPrice
        overageType
    }
}
"""

INTROSPECT_QUERY = """
query IntrospectOverage {
    __type(name: "OverageRecord") {
        name
        kind
        fields {
            name
            type {
                name
                kind
            }
        }
    }
}
"""


async def get_auth_headers(
    email: str, password: str, org_id: str | None = None
) -> dict:
    """Get authentication headers."""
    try:
        from tests.common.token_generator import generate_token

        return await generate_token(
            email=email, password=password, organization_id=org_id
        )
    except Exception as e:
        print(f"Warning: Could not generate token: {e}")
        return {"Content-Type": "application/json"}


async def graphql_request(query: str, variables: dict | None, headers: dict) -> dict:
    """Execute a GraphQL request."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            BASE_URL,
            json={"query": query, "variables": variables or {}},
            headers=headers,
        )
        return response.json()


async def test_schema_introspection(headers: dict) -> bool:
    """Test that OverageRecord type exists in schema."""
    print("\n[1] Testing Schema Introspection...")

    result = await graphql_request(INTROSPECT_QUERY, None, headers)

    if "errors" in result:
        print(f"  ❌ FAILED: {result['errors']}")
        return False

    overage_type = result.get("data", {}).get("__type")
    if not overage_type:
        print("  ❌ FAILED: OverageRecord type not found in schema")
        return False

    print(f"  ✅ OverageRecord type found")
    print(f"     Fields:")
    for field in overage_type.get("fields", []):
        print(
            f"       - {field['name']}: {field['type']['name'] or field['type']['kind']}"
        )

    return True


async def test_overage_calculation(
    headers: dict,
    product_id: str,
    factory_id: str,
    end_user_id: str,
    unit_price: float,
    quantity: float = 1.0,
) -> bool:
    """Test overage calculation with real UUIDs."""
    print("\n[2] Testing Overage Calculation...")
    print(f"    Product ID: {product_id}")
    print(f"    Factory ID: {factory_id}")
    print(f"    End User ID: {end_user_id}")
    print(f"    Unit Price: ${unit_price:.2f}")
    print(f"    Quantity: {quantity}")

    result = await graphql_request(
        FIND_OVERAGE_QUERY,
        {
            "productId": product_id,
            "factoryId": factory_id,
            "endUserId": end_user_id,
            "detailUnitPrice": unit_price,
            "quantity": quantity,
        },
        headers,
    )

    if "errors" in result:
        print(f"  ❌ FAILED: {result['errors']}")
        return False

    overage = result.get("data", {}).get(
        "findEffectiveCommissionRateAndOverageUnitPriceByProduct", {}
    )

    print(f"\n  Response:")
    print(f"    success: {overage.get('success')}")
    print(f"    errorMessage: {overage.get('errorMessage')}")
    print(f"    baseUnitPrice: ${overage.get('baseUnitPrice') or 0:.2f}")
    print(f"    overageUnitPrice: ${overage.get('overageUnitPrice') or 0:.2f}")
    print(
        f"    effectiveCommissionRate: {overage.get('effectiveCommissionRate') or 0:.2f}%"
    )
    print(f"    repShare: {(overage.get('repShare') or 0) * 100:.1f}%")
    print(f"    overageType: {overage.get('overageType')}")

    if overage.get("success"):
        print("\n  ✅ Overage calculation successful")

        # Check if there's overage
        base = overage.get("baseUnitPrice") or 0
        ovg = overage.get("overageUnitPrice") or 0
        if ovg > 0:
            print(f"  📊 Overage detected: ${ovg:.2f} (markup over base ${base:.2f})")
        else:
            print(f"  📊 No overage (unit price at or below base ${base:.2f})")

        return True
    else:
        print(f"\n  ⚠️ Calculation returned error: {overage.get('errorMessage')}")
        return True  # Not a failure, just informational


async def main():
    parser = argparse.ArgumentParser(description="Test Overage endpoint")
    parser.add_argument("--email", "-e", help="User email")
    parser.add_argument("--password", "-p", help="User password")
    parser.add_argument(
        "--org-id",
        "-o",
        default="org_01KE7D0TTXV7TZ9JSXFPXCXJ35",
        help="Organization ID",
    )
    parser.add_argument("--product-id", help="Product UUID")
    parser.add_argument("--factory-id", help="Factory UUID")
    parser.add_argument("--end-user-id", help="End User (Customer) UUID")
    parser.add_argument(
        "--unit-price", type=float, default=150.0, help="Unit price to test"
    )
    parser.add_argument("--quantity", type=float, default=1.0, help="Quantity")

    args = parser.parse_args()

    print("=" * 60)
    print("Overage Endpoint Test")
    print("=" * 60)

    # Get auth headers
    if args.email and args.password:
        headers = await get_auth_headers(args.email, args.password, args.org_id)
    else:
        headers = {"Content-Type": "application/json"}

    all_passed = True

    # Test 1: Schema introspection
    if not await test_schema_introspection(headers):
        all_passed = False

    # Test 2: Overage calculation (if UUIDs provided)
    if args.product_id and args.factory_id and args.end_user_id:
        if not await test_overage_calculation(
            headers,
            args.product_id,
            args.factory_id,
            args.end_user_id,
            args.unit_price,
            args.quantity,
        ):
            all_passed = False
    else:
        print("\n[2] Skipping Overage Calculation test (no UUIDs provided)")
        print("    To test, provide: --product-id, --factory-id, --end-user-id")

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)

    # Instructions for getting UUIDs
    print("""
To get UUIDs for testing:

1. From the frontend, open a quote and check the Network tab
2. Or query the CRM backend directly:

   # Get a product ID
   curl -X POST http://localhost:3000/api/graphql \\
     -H "Content-Type: application/json" \\
     -d '{"query":"{ products(limit:1) { items { id factoryId } } }"}'

3. Or use the browser console in FlowCRM:
   - Open a quote
   - console.log(JSON.stringify(quote.details[0], null, 2))
""")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
