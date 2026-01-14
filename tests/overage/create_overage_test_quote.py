#!/usr/bin/env python3
"""
Create a test quote with overage for frontend testing.

This script:
1. Enables overage for a factory (requires DB access)
2. Creates/finds a product with a base price
3. Creates a quote with markup price to generate overage
4. The quote can then be viewed in the frontend Overage View

Requirements:
- CRM backend access (staging.v6.api.flowrms.com)
- Database access to enable overage (pycore schema)
- Valid authentication credentials

Usage:
    cd /home/jorge/flowrms/FLO-727/flow-py-backend

    # Step 1: Enable overage for factory (run this SQL manually or provide DB_URL)
    # See the SQL output from this script

    # Step 2: Create test quote
    uv run python tests/overage/create_overage_test_quote.py \
        --email jorge@flowrms.com \
        --password 'CucoHermoso2026$' \
        --create-quote

    # Or do everything if you have DB access
    uv run python tests/overage/create_overage_test_quote.py \
        --email jorge@flowrms.com \
        --password 'CucoHermoso2026$' \
        --db-url "postgresql://user:pass@host/db" \
        --full-setup
"""
import argparse
import asyncio
import sys
from pathlib import Path
from decimal import Decimal
from uuid import uuid4
from datetime import date

import httpx

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Use local backend (flow-py-backend) which has fixtureSchedule support
CRM_URL = "http://localhost:5555/graphql"

# Test data
FACTORY_ID = "bdc26ef9-c5c0-4d78-885a-49d026ee042b"  # COOPER LIGHTING LLC
FACTORY_NAME = "COOPER LIGHTING LLC"
CUSTOMER_ID = "c373f3df-702b-46c4-b3de-d64f64087672"  # SOUTHERN ACCOUNTS PAYABLE-MPC
UOM_ID = "f924255f-092a-4f1e-bd71-cc8454c6e6b7"  # "ea" (each)

# Product to create for testing
TEST_PRODUCT = {
    "factoryPartNumber": f"TEST-OVERAGE-{uuid4().hex[:6].upper()}",
    "description": "Test Product for Overage View Testing",
    "unitPrice": "100.00",  # Base price $100
    "defaultCommissionRate": "10.00",  # 10% commission
    "productUomId": UOM_ID,
}

# Quote prices (with markup to generate overage)
QUOTE_DETAILS = [
    {"markup": 1.20, "qty": 1, "fixture": "TYPE_A"},  # 20% markup = $20 overage
    {"markup": 1.50, "qty": 2, "fixture": "TYPE_B"},  # 50% markup = $50 overage
    {"markup": 1.10, "qty": 5, "fixture": "TYPE_C"},  # 10% markup = $10 overage
]


async def get_auth_headers(email: str, password: str, org_id: str = "org_01KE7D0TTXV7TZ9JSXFPXCXJ35") -> dict:
    """Get authentication headers."""
    from tests.common.token_generator import generate_token
    return await generate_token(email=email, password=password, organization_id=org_id)


async def graphql_request(query: str, variables: dict | None, headers: dict) -> dict:
    """Execute a GraphQL request."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            CRM_URL,
            json={"query": query, "variables": variables or {}},
            headers=headers,
        )
        return response.json()


def print_sql_for_overage():
    """Print SQL to enable overage for the factory."""
    print("\n" + "=" * 70)
    print("SQL TO ENABLE OVERAGE FOR COOPER LIGHTING LLC")
    print("=" * 70)
    print("""
Run this SQL in your database (pycore schema):

-- Enable overage for COOPER LIGHTING LLC
UPDATE pycore.factories
SET overage_allowed = true,
    overage_type = 0,           -- 0 = BY_LINE, 1 = BY_TOTAL
    rep_overage_share = 100.00  -- 100% of overage goes to rep
WHERE id = 'bdc26ef9-c5c0-4d78-885a-49d026ee042b';

-- Verify the update
SELECT id, title, overage_allowed, overage_type, rep_overage_share
FROM pycore.factories
WHERE id = 'bdc26ef9-c5c0-4d78-885a-49d026ee042b';

-- If you also need to set a base price on a product:
UPDATE pycore.products
SET unit_price = 100.00,
    default_commission_rate = 10.00
WHERE factory_id = 'bdc26ef9-c5c0-4d78-885a-49d026ee042b'
AND unit_price IS NULL OR unit_price = 0
LIMIT 5;
""")
    print("=" * 70 + "\n")


async def enable_overage_db(db_url: str) -> bool:
    """Enable overage for factory using direct DB connection."""
    try:
        from sqlalchemy import create_engine, text

        # Convert asyncpg URL to psycopg2 if needed
        sync_url = db_url.replace("+asyncpg", "")

        engine = create_engine(sync_url)

        with engine.connect() as conn:
            # Check if factory exists
            result = conn.execute(
                text("SELECT title, overage_allowed FROM pycore.factories WHERE id = :id"),
                {"id": FACTORY_ID}
            )
            row = result.fetchone()

            if not row:
                print(f"Factory {FACTORY_ID} not found")
                return False

            print(f"Factory: {row[0]}, Current overage_allowed: {row[1]}")

            # Enable overage
            conn.execute(
                text("""
                    UPDATE pycore.factories
                    SET overage_allowed = true,
                        overage_type = 0,
                        rep_overage_share = 100.00
                    WHERE id = :id
                """),
                {"id": FACTORY_ID}
            )
            conn.commit()

            print(f"✅ Overage enabled for {FACTORY_NAME}")
            return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        print("Make sure DB_URL points to a database with pycore schema")
        return False


async def create_test_product(headers: dict) -> str | None:
    """Create a test product with a base price."""
    print("\n[1] Creating test product...")

    mutation = """
    mutation CreateProduct($input: ProductInput!) {
        createProduct(input: $input) {
            id
            factoryPartNumber
            unitPrice
            defaultCommissionRate
        }
    }
    """

    variables = {
        "input": {
            "factoryId": FACTORY_ID,
            "factoryPartNumber": TEST_PRODUCT["factoryPartNumber"],
            "description": TEST_PRODUCT["description"],
            "unitPrice": TEST_PRODUCT["unitPrice"],
            "defaultCommissionRate": TEST_PRODUCT["defaultCommissionRate"],
            "productUomId": TEST_PRODUCT["productUomId"],
            "published": True,
        }
    }

    result = await graphql_request(mutation, variables, headers)

    if 'errors' in result:
        print(f"  ❌ Failed to create product: {result['errors']}")
        return None

    product = result.get('data', {}).get('createProduct', {})
    if product:
        print(f"  ✅ Created product: {product['factoryPartNumber']}")
        print(f"     ID: {product['id']}")
        print(f"     Base Price: ${product['unitPrice']}")
        print(f"     Commission Rate: {product['defaultCommissionRate']}%")
        return product['id']

    return None


async def find_or_create_product(headers: dict) -> tuple[str, float] | None:
    """Find an existing product with price or create one."""
    print("\n[1] Finding product with price...")

    # First try to find existing product
    query = """
    query FindProduct($factoryId: UUID!) {
        productSearch(searchTerm: "TEST-OVERAGE", factoryId: $factoryId, limit: 1) {
            id
            factoryPartNumber
            unitPrice
        }
    }
    """

    result = await graphql_request(
        query,
        {"factoryId": FACTORY_ID},
        headers
    )

    if 'data' in result:
        products = result['data'].get('productSearch', [])
        for p in products:
            price = float(p.get('unitPrice') or 0)
            if price > 0:
                print(f"  ✅ Found existing product: {p['factoryPartNumber']}")
                print(f"     ID: {p['id']}")
                print(f"     Base Price: ${price:.2f}")
                return p['id'], price

    # If not found, create one
    print("  No existing test product found. Creating new one...")
    product_id = await create_test_product(headers)
    if product_id:
        return product_id, float(TEST_PRODUCT["unitPrice"])

    return None


async def create_test_quote(headers: dict, product_id: str, base_price: float) -> str | None:
    """Create a test quote with markup prices for overage testing."""
    print("\n[2] Creating test quote with overage line items...")

    quote_number = f"OVERAGE-TEST-{uuid4().hex[:8].upper()}"

    # Build line items with markup prices
    details = []
    for i, item in enumerate(QUOTE_DETAILS):
        markup_price = base_price * item["markup"]
        overage_amount = markup_price - base_price

        details.append({
            "productId": product_id,
            "factoryId": FACTORY_ID,  # Factory at detail level
            "endUserId": CUSTOMER_ID,  # End user at detail level
            "quantity": item["qty"],
            "unitPrice": str(round(markup_price, 2)),
            "itemNumber": i + 1,
            "fixtureSchedule": item["fixture"],  # Now supported in flow-py-backend!
        })

        print(f"  Line {i+1}: ${markup_price:.2f} (base: ${base_price:.2f}, overage: ${overage_amount:.2f}) - {item['fixture']}")

    mutation = """
    mutation CreateQuote($input: QuoteInput!) {
        createQuote(input: $input) {
            id
            quoteNumber
            details {
                id
                unitPrice
                fixtureSchedule
                overageUnitPrice
                overageCommissionRate
            }
        }
    }
    """

    variables = {
        "input": {
            "quoteNumber": quote_number,
            "entityDate": str(date.today()),
            "soldToCustomerId": CUSTOMER_ID,
            "status": "OPEN",
            "pipelineStage": "DISCOVERY",
            "published": True,
            "creationType": "MANUAL",
            "blanket": False,
            "details": details,
        }
    }

    result = await graphql_request(mutation, variables, headers)

    if 'errors' in result:
        print(f"\n  ❌ Failed to create quote: {result['errors']}")

        # Check if it's a field error
        for error in result.get('errors', []):
            msg = error.get('message', '')
            if 'field' in msg.lower():
                print(f"  Hint: Check the QuoteInput schema for required fields")

        return None

    quote = result.get('data', {}).get('createQuote', {})
    if quote:
        print(f"\n  ✅ Created quote: {quote['quoteNumber']}")
        print(f"     ID: {quote['id']}")
        print(f"     Line Items: {len(quote.get('details', []))}")

        print("\n" + "=" * 70)
        print("SUCCESS! Quote created for Overage View testing")
        print("=" * 70)
        print(f"""
To test in the frontend:

1. Open FlowCRM: https://staging.console.flowrms.com
2. Navigate to Quotes
3. Search for: {quote['quoteNumber']}
4. Open the quote
5. Switch to "Overage View" in the dropdown

Expected behavior:
- Overage columns should show calculated values
- Each line item should show:
  - Base price: ${base_price:.2f}
  - Overage amounts based on markup
  - Fixture Schedule: TYPE_A, TYPE_B, TYPE_C
""")
        print("=" * 70)

        return quote['id']

    return None


async def main():
    parser = argparse.ArgumentParser(
        description="Create test quote for Overage View testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--email", "-e", required=True, help="User email")
    parser.add_argument("--password", "-p", required=True, help="User password")
    parser.add_argument("--org-id", default="org_01KE7D0TTXV7TZ9JSXFPXCXJ35", help="Organization ID")
    parser.add_argument("--db-url", help="Database URL for enabling overage")
    parser.add_argument("--create-quote", action="store_true", help="Create test quote")
    parser.add_argument("--full-setup", action="store_true", help="Enable overage + create quote")
    parser.add_argument("--show-sql", action="store_true", help="Show SQL for enabling overage")

    args = parser.parse_args()

    if args.show_sql:
        print_sql_for_overage()
        return

    # Get auth headers
    print("Authenticating...")
    headers = await get_auth_headers(args.email, args.password, args.org_id)

    if args.full_setup and args.db_url:
        # Enable overage in DB
        print("\n[0] Enabling overage for factory...")
        if not await enable_overage_db(args.db_url):
            print("\n⚠️  Could not enable overage. Run SQL manually:")
            print_sql_for_overage()

    if args.create_quote or args.full_setup:
        # Find or create product
        result = await find_or_create_product(headers)
        if not result:
            print("\n❌ Could not find or create product")
            print_sql_for_overage()
            return

        product_id, base_price = result

        # Create quote
        quote_id = await create_test_quote(headers, product_id, base_price)
        if not quote_id:
            print("\n❌ Failed to create quote")
            return

        print("\n✅ Test setup complete!")

    else:
        parser.print_help()
        print("\n" + "-" * 70)
        print("Quick Start:")
        print("-" * 70)
        print("""
1. First, enable overage for COOPER LIGHTING LLC:
   uv run python tests/overage/create_overage_test_quote.py --show-sql

2. Run the SQL shown above in your database

3. Then create the test quote:
   uv run python tests/overage/create_overage_test_quote.py \\
       --email jorge@flowrms.com \\
       --password 'CucoHermoso2026$' \\
       --create-quote
""")


if __name__ == "__main__":
    asyncio.run(main())
