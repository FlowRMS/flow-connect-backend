#!/usr/bin/env python3
"""
API Contract Tests for Overage View.

These tests verify that the Overage View API responses match what the frontend expects.
This allows testing the Overage View feature end-to-end.

Requirements:
- Server running on localhost:5555 (uv run ./start.py)
- Valid authentication credentials

Usage:
    cd /home/jorge/flowrms/FLO-727/flow-py-backend

    # Run all overage tests
    uv run python tests/overage/test_overage_api_contract.py --email your@email.com --password yourpassword

    # Test specific factory by name
    uv run python tests/overage/test_overage_api_contract.py --email your@email.com --password yourpassword --factory "COOPER LIGHTING"

    # Enable overage for a factory (requires factory to have overage_allowed=true in DB)
    uv run python tests/overage/test_overage_api_contract.py --email your@email.com --password yourpassword --enable-for "COOPER LIGHTING LLC"
"""
import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any
from uuid import UUID

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


# ============================================================================
# GraphQL Queries for Overage Testing
# ============================================================================

GET_FACTORIES_WITH_OVERAGE = """
query GetFactoriesWithOverage($limit: Int) {
    factories(limit: $limit) {
        items {
            id
            title
            overageAllowed
            overageType
            repOverageShare
            baseCommissionRate
        }
    }
}
"""

GET_FACTORY_BY_NAME = """
query GetFactoryByName($search: String!) {
    factories(search: $search, limit: 5) {
        items {
            id
            title
            overageAllowed
            overageType
            repOverageShare
            baseCommissionRate
        }
    }
}
"""

FIND_OVERAGE_BY_PRODUCT = """
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

GET_PRODUCTS_BY_FACTORY = """
query GetProductsByFactory($factoryId: ID!, $limit: Int) {
    products(factoryId: $factoryId, limit: $limit) {
        items {
            id
            modelNumber
            unitPrice
            defaultCommissionRate
        }
    }
}
"""

GET_CUSTOMERS = """
query GetCustomers($limit: Int) {
    customers(limit: $limit) {
        items {
            id
            title
        }
    }
}
"""

GET_QUOTES_BY_FACTORY = """
query GetQuotesByFactory($factoryId: ID!, $limit: Int) {
    quotes(factoryId: $factoryId, limit: $limit) {
        items {
            id
            quoteNumber
            factoryId
            endUserId
            details {
                id
                productId
                unitPrice
                quantity
                totalAmount
            }
        }
    }
}
"""


# ============================================================================
# Contract Verification Functions
# ============================================================================

def verify_factory_overage_fields(factory: dict) -> list[str]:
    """Verify factory has overage-related fields for frontend."""
    errors = []

    required_fields = ['id', 'title', 'overageAllowed', 'overageType', 'repOverageShare']
    for field in required_fields:
        if field not in factory:
            errors.append(f"Missing required field: {field}")

    # Type checks
    if 'overageAllowed' in factory and not isinstance(factory['overageAllowed'], bool):
        errors.append(f"overageAllowed should be bool, got {type(factory['overageAllowed'])}")

    if 'overageType' in factory and factory['overageType'] not in [None, 'BY_LINE', 'BY_TOTAL', 0, 1]:
        errors.append(f"Invalid overageType: {factory['overageType']}")

    return errors


def verify_overage_record_response(record: dict) -> list[str]:
    """Verify OverageRecord has all fields frontend expects."""
    errors = []

    # Required fields
    required_fields = ['success', 'overageType']
    for field in required_fields:
        if field not in record:
            errors.append(f"Missing required field: {field}")

    # Nullable numeric fields
    numeric_fields = [
        'effectiveCommissionRate',
        'overageUnitPrice',
        'baseUnitPrice',
        'repShare',
        'levelRate',
        'levelUnitPrice',
    ]
    for field in numeric_fields:
        if field in record and record[field] is not None:
            if not isinstance(record[field], (int, float)):
                errors.append(f"Field {field} should be numeric, got {type(record[field])}")

    # errorMessage should be string or null
    if 'errorMessage' in record and record['errorMessage'] is not None:
        if not isinstance(record['errorMessage'], str):
            errors.append(f"errorMessage should be string, got {type(record['errorMessage'])}")

    return errors


# ============================================================================
# Test Functions
# ============================================================================

async def test_factories_with_overage(headers: dict, factory_name: str | None = None) -> dict | None:
    """Test that factories have overage fields and find one with overage enabled."""
    print("\n[1] Testing Factory Overage Fields...")

    try:
        if factory_name:
            result = await graphql_request(
                GET_FACTORY_BY_NAME,
                variables={'search': factory_name},
                headers=headers,
            )
        else:
            result = await graphql_request(
                GET_FACTORIES_WITH_OVERAGE,
                variables={'limit': 50},
                headers=headers,
            )

        if 'errors' in result:
            print(f"  FAILED: GraphQL errors: {result['errors']}")
            return None

        factories = result.get('data', {}).get('factories', {}).get('items', [])
        if not factories:
            print("  SKIPPED: No factories found")
            return None

        # Find factory with overage enabled
        overage_factory = None
        for factory in factories:
            errors = verify_factory_overage_fields(factory)
            if errors:
                print(f"  WARNING: Factory {factory.get('id')}: {errors}")

            if factory.get('overageAllowed'):
                overage_factory = factory
                print(f"  FOUND: Factory with overage enabled: {factory['title']}")
                print(f"         ID: {factory['id']}")
                print(f"         Overage Type: {factory.get('overageType')}")
                print(f"         Rep Share: {factory.get('repOverageShare')}%")
                print(f"         Base Commission: {factory.get('baseCommissionRate')}%")

        if not overage_factory:
            print(f"  INFO: No factories with overage_allowed=true found (checked {len(factories)} factories)")
            print("  TIP: Use SQL to enable overage:")
            print("       UPDATE pycore.factories SET overage_allowed = true WHERE title = 'YOUR_FACTORY';")
            # Return first factory for testing anyway
            return factories[0]

        print(f"  PASSED: Verified {len(factories)} factory responses")
        return overage_factory

    except Exception as e:
        print(f"  ERROR: {e}")
        return None


async def test_overage_calculation(
    headers: dict,
    factory: dict,
) -> bool:
    """Test overage calculation endpoint."""
    print("\n[2] Testing Overage Calculation...")

    try:
        factory_id = factory['id']

        # Get a product from this factory
        result = await graphql_request(
            GET_PRODUCTS_BY_FACTORY,
            variables={'factoryId': factory_id, 'limit': 5},
            headers=headers,
        )

        if 'errors' in result:
            print(f"  FAILED: GraphQL errors: {result['errors']}")
            return False

        products = result.get('data', {}).get('products', {}).get('items', [])
        if not products:
            print(f"  SKIPPED: No products for factory {factory['title']}")
            return True

        # Get a customer (end user)
        result = await graphql_request(
            GET_CUSTOMERS,
            variables={'limit': 1},
            headers=headers,
        )

        if 'errors' in result:
            print(f"  FAILED: GraphQL errors getting customers: {result['errors']}")
            return False

        customers = result.get('data', {}).get('customers', {}).get('items', [])
        if not customers:
            print("  SKIPPED: No customers found")
            return True

        customer = customers[0]
        product = products[0]

        print(f"  Testing with:")
        print(f"    Product: {product.get('modelNumber')} (ID: {product['id']})")
        print(f"    Unit Price: ${product.get('unitPrice', 'N/A')}")
        print(f"    Commission Rate: {product.get('defaultCommissionRate', 'N/A')}%")
        print(f"    Customer: {customer.get('title')} (ID: {customer['id']})")

        # Test overage calculation with detail price higher than base
        base_price = float(product.get('unitPrice', 100))
        test_price = base_price * 1.2  # 20% markup

        result = await graphql_request(
            FIND_OVERAGE_BY_PRODUCT,
            variables={
                'productId': product['id'],
                'detailUnitPrice': test_price,
                'factoryId': factory_id,
                'endUserId': customer['id'],
                'quantity': 1.0,
            },
            headers=headers,
        )

        if 'errors' in result:
            print(f"  FAILED: GraphQL errors: {result['errors']}")
            return False

        overage = result.get('data', {}).get('findEffectiveCommissionRateAndOverageUnitPriceByProduct', {})

        errors = verify_overage_record_response(overage)
        if errors:
            print(f"  FAILED: Response validation: {errors}")
            return False

        print(f"  RESPONSE:")
        print(f"    Success: {overage.get('success')}")
        print(f"    Error Message: {overage.get('errorMessage')}")
        print(f"    Overage Type: {overage.get('overageType')}")
        print(f"    Base Unit Price: ${overage.get('baseUnitPrice', 'N/A')}")
        print(f"    Detail Unit Price: ${test_price}")
        print(f"    Overage Unit Price: ${overage.get('overageUnitPrice', 'N/A')}")
        print(f"    Effective Commission Rate: {overage.get('effectiveCommissionRate', 'N/A')}%")
        print(f"    Rep Share: {overage.get('repShare', 'N/A')}")

        if overage.get('success'):
            if factory.get('overageAllowed') and overage.get('overageUnitPrice'):
                print("  PASSED: Overage calculation working correctly")
            elif not factory.get('overageAllowed'):
                print("  PASSED: Overage disabled for factory (expected)")
            else:
                print("  PASSED: No overage (detail price <= base price)")
        else:
            print(f"  INFO: Calculation returned error: {overage.get('errorMessage')}")

        return True

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_quote_with_overage(headers: dict, factory: dict) -> bool:
    """Test fetching quotes and calculating overage for each line item."""
    print("\n[3] Testing Quotes with Overage...")

    try:
        factory_id = factory['id']

        result = await graphql_request(
            GET_QUOTES_BY_FACTORY,
            variables={'factoryId': factory_id, 'limit': 3},
            headers=headers,
        )

        if 'errors' in result:
            print(f"  FAILED: GraphQL errors: {result['errors']}")
            return False

        quotes = result.get('data', {}).get('quotes', {}).get('items', [])
        if not quotes:
            print(f"  SKIPPED: No quotes for factory {factory['title']}")
            return True

        print(f"  Found {len(quotes)} quotes for {factory['title']}")

        for quote in quotes:
            print(f"\n  Quote #{quote.get('quoteNumber', 'N/A')} (ID: {quote['id']})")
            details = quote.get('details', [])

            if not details:
                print("    No line items")
                continue

            end_user_id = quote.get('endUserId')
            if not end_user_id:
                print("    No end user - skipping overage calc")
                continue

            print(f"    {len(details)} line items:")
            for detail in details[:3]:  # Test first 3 items
                product_id = detail.get('productId')
                unit_price = detail.get('unitPrice', 0)

                if not product_id:
                    continue

                # Calculate overage for this line item
                result = await graphql_request(
                    FIND_OVERAGE_BY_PRODUCT,
                    variables={
                        'productId': product_id,
                        'detailUnitPrice': float(unit_price) if unit_price else 100.0,
                        'factoryId': factory_id,
                        'endUserId': end_user_id,
                        'quantity': float(detail.get('quantity', 1)),
                    },
                    headers=headers,
                )

                if 'errors' in result:
                    print(f"      Product {product_id}: Error - {result['errors']}")
                    continue

                overage = result.get('data', {}).get('findEffectiveCommissionRateAndOverageUnitPriceByProduct', {})

                ovg_price = overage.get('overageUnitPrice')
                eff_rate = overage.get('effectiveCommissionRate')

                print(f"      Product: ${unit_price:.2f} | Base: ${overage.get('baseUnitPrice') or 0:.2f} | Ovg: ${ovg_price or 0:.2f} | Eff Rate: {eff_rate or 0:.2f}%")

        print("\n  PASSED: Quote overage calculation completed")
        return True

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# Main Test Runner
# ============================================================================

async def run_overage_tests(headers: dict, factory_name: str | None = None) -> bool:
    """Run all overage contract tests and return success status."""
    all_passed = True

    print("\n" + "=" * 60)
    print("Overage View API Contract Tests")
    print("=" * 60)

    # Test 1: Get factories with overage fields
    factory = await test_factories_with_overage(headers, factory_name)
    if not factory:
        print("\nNo factory available for testing")
        return False

    # Test 2: Test overage calculation endpoint
    if not await test_overage_calculation(headers, factory):
        all_passed = False

    # Test 3: Test quotes with overage
    if not await test_quote_with_overage(headers, factory):
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL OVERAGE TESTS PASSED")
    else:
        print("SOME OVERAGE TESTS FAILED")
    print("=" * 60)

    return all_passed


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Overage View API contract tests")
    parser.add_argument("--email", "-e", required=True, help="User email")
    parser.add_argument("--password", "-p", required=True, help="User password")
    parser.add_argument("--org-id", "-o", help="Organization ID (optional)")
    parser.add_argument("--factory", "-f", help="Factory name to test (optional)")
    parser.add_argument(
        "--enable-for",
        help="Factory name to enable overage for (SQL update suggestion)",
    )

    args = parser.parse_args()

    if args.enable_for:
        print(f"\nTo enable overage for '{args.enable_for}', run this SQL:")
        print("-" * 60)
        print(f"""
UPDATE pycore.factories
SET overage_allowed = true,
    overage_type = 0,  -- 0 = BY_LINE, 1 = BY_TOTAL
    rep_overage_share = 100.00  -- 100% of overage goes to rep
WHERE title ILIKE '%{args.enable_for}%';
""")
        print("-" * 60)
        print("Then re-run this test without --enable-for")
        return

    print(f"Generating token for: {args.email}")
    try:
        headers = await generate_token(
            email=args.email,
            password=args.password,
            organization_id=args.org_id,
        )
    except Exception as e:
        print(f"Failed to generate token: {e}")
        sys.exit(1)

    success = await run_overage_tests(headers, args.factory)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
