#!/usr/bin/env python3
import asyncio

import httpx

BASE_URL = "http://localhost:5555/graphql"

QUERY = """
query FindEffectiveCommissionRateAndOverage(
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
    effectiveCommissionRate
    overageUnitPrice
    baseUnitPrice
    repShare
    levelRate
    levelUnitPrice
    overageType
    errorMessage
    success
  }
}
"""


async def test_without_auth():
    """Test without any auth headers (like the passing test)."""
    print("\n[1] Testing WITHOUT authentication headers...")
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            BASE_URL,
            json={
                "query": QUERY,
                "variables": {
                    "productId": "b9f9d8a5-d02c-40ce-9e6a-be3fdc9972fd",
                    "detailUnitPrice": 120.0,
                    "factoryId": "bdc26ef9-c5c0-4d78-885a-49d026ee042b",
                    "endUserId": "c373f3df-702b-46c4-b3de-d64f64087672",
                    "quantity": 1.0,
                },
            },
            headers=headers,
        )
        result = response.json()
        print(f"  Status: {response.status_code}")
        print(f"  Response: {result}")
        return result


async def test_with_fake_auth():
    """Test with auth headers similar to what frontend sends."""
    print("\n[2] Testing WITH authentication headers (fake token)...")
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer fake-token-12345",
        "x-auth-provider": "WORKOS",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            BASE_URL,
            json={
                "query": QUERY,
                "variables": {
                    "productId": "b9f9d8a5-d02c-40ce-9e6a-be3fdc9972fd",
                    "detailUnitPrice": 120.0,
                    "factoryId": "bdc26ef9-c5c0-4d78-885a-49d026ee042b",
                    "endUserId": "c373f3df-702b-46c4-b3de-d64f64087672",
                    "quantity": 1.0,
                },
            },
            headers=headers,
        )
        result = response.json()
        print(f"  Status: {response.status_code}")
        print(f"  Response: {result}")
        return result


async def main():
    print("=" * 60)
    print("Frontend Simulation Test")
    print("=" * 60)

    # Test 1: Without auth
    result1 = await test_without_auth()

    # Test 2: With fake auth
    result2 = await test_with_fake_auth()

    print("\n" + "=" * 60)
    print("COMPARISON:")
    print("=" * 60)

    has_data_1 = (
        result1.get("data") is not None
        and result1["data"].get(
            "findEffectiveCommissionRateAndOverageUnitPriceByProduct"
        )
        is not None
    )
    has_data_2 = (
        result2.get("data") is not None
        and result2["data"].get(
            "findEffectiveCommissionRateAndOverageUnitPriceByProduct"
        )
        is not None
    )

    print(f"Without auth: {'✅ SUCCESS' if has_data_1 else '❌ FAILED'}")
    print(f"With auth:    {'✅ SUCCESS' if has_data_2 else '❌ FAILED'}")

    if not has_data_2 and "errors" in result2:
        print(f"\nError with auth: {result2['errors']}")


if __name__ == "__main__":
    asyncio.run(main())
