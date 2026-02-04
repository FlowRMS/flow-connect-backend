#!/usr/bin/env python3
"""
Setup script for Overage View frontend testing.

This script prepares the database with test data for the Overage View feature:
1. Enables overage for a specific factory
2. Sets up products with base prices for overage calculations
3. Optionally creates a test quote with line items

Requirements:
- Database connection configured in environment
- Valid authentication credentials for API calls

Usage:
    cd /home/jorge/flowrms/FLO-727/flow-py-backend

    # Enable overage for a factory
    uv run python tests/overage/setup_overage_test_data.py --enable-overage "COOPER LIGHTING LLC"

    # Check factory overage status
    uv run python tests/overage/setup_overage_test_data.py --check "COOPER LIGHTING LLC"

    # Create a test quote with overage line items
    uv run python tests/overage/setup_overage_test_data.py --create-quote --factory "COOPER LIGHTING LLC" --email your@email.com --password yourpassword

    # Full setup: enable overage + create test quote
    uv run python tests/overage/setup_overage_test_data.py --full-setup --factory "COOPER LIGHTING LLC" --email your@email.com --password yourpassword
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path
from uuid import uuid4

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import httpx

# Try to import database modules
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("WARNING: SQLAlchemy not available. Database operations disabled.")

# API base URL
BASE_URL = "http://localhost:5555/graphql"


# ============================================================================
# Database Operations
# ============================================================================

def get_database_url() -> str:
    """Get database URL from environment."""
    # Try different environment variable names
    for var in ['DATABASE_URL', 'NEON_DATABASE_URL', 'POSTGRES_URL']:
        url = os.environ.get(var)
        if url:
            return url

    # Default Neon connection (update with your actual URL)
    raise ValueError(
        "No database URL found. Set DATABASE_URL environment variable.\n"
        "Example: export DATABASE_URL='postgresql://user:pass@host/db'"
    )


def enable_overage_for_factory(factory_name: str, overage_type: int = 0, rep_share: float = 100.0) -> bool:
    """
    Enable overage for a factory in the database.

    Args:
        factory_name: Factory title (case-insensitive search)
        overage_type: 0 = BY_LINE, 1 = BY_TOTAL
        rep_share: Percentage of overage that goes to rep (0-100)
    """
    if not DB_AVAILABLE:
        print("Database modules not available")
        return False

    try:
        db_url = get_database_url()
        engine = create_engine(db_url)

        with engine.connect() as conn:
            # First, find the factory
            result = conn.execute(
                text("SELECT id, title, overage_allowed, overage_type, rep_overage_share FROM pycore.factories WHERE title ILIKE :name"),
                {"name": f"%{factory_name}%"}
            )
            rows = result.fetchall()

            if not rows:
                print(f"No factory found matching '{factory_name}'")
                return False

            if len(rows) > 1:
                print(f"Multiple factories found matching '{factory_name}':")
                for row in rows:
                    print(f"  - {row[1]} (ID: {row[0]})")
                print("Please use a more specific name.")
                return False

            factory_id, title, current_overage, current_type, current_share = rows[0]

            print(f"\nFactory: {title}")
            print(f"  ID: {factory_id}")
            print(f"  Current overage_allowed: {current_overage}")
            print(f"  Current overage_type: {current_type} ({'BY_LINE' if current_type == 0 else 'BY_TOTAL'})")
            print(f"  Current rep_overage_share: {current_share}%")

            # Update the factory
            conn.execute(
                text("""
                    UPDATE pycore.factories
                    SET overage_allowed = true,
                        overage_type = :overage_type,
                        rep_overage_share = :rep_share
                    WHERE id = :factory_id
                """),
                {
                    "factory_id": factory_id,
                    "overage_type": overage_type,
                    "rep_share": rep_share,
                }
            )
            conn.commit()

            print(f"\n✅ Updated factory '{title}':")
            print(f"  overage_allowed: true")
            print(f"  overage_type: {overage_type} ({'BY_LINE' if overage_type == 0 else 'BY_TOTAL'})")
            print(f"  rep_overage_share: {rep_share}%")

            return True

    except Exception as e:
        print(f"Error: {e}")
        return False


def check_factory_overage(factory_name: str) -> dict | None:
    """Check overage configuration for a factory."""
    if not DB_AVAILABLE:
        print("Database modules not available")
        return None

    try:
        db_url = get_database_url()
        engine = create_engine(db_url)

        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, title, overage_allowed, overage_type, rep_overage_share, base_commission_rate
                    FROM pycore.factories
                    WHERE title ILIKE :name
                """),
                {"name": f"%{factory_name}%"}
            )
            rows = result.fetchall()

            if not rows:
                print(f"No factory found matching '{factory_name}'")
                return None

            print(f"\nFactories matching '{factory_name}':\n")
            for row in rows:
                factory_id, title, overage_allowed, overage_type, rep_share, base_rate = row
                overage_type_str = 'BY_LINE' if overage_type == 0 else 'BY_TOTAL' if overage_type == 1 else 'N/A'
                status = '✅ ENABLED' if overage_allowed else '❌ DISABLED'

                print(f"  {title}")
                print(f"    ID: {factory_id}")
                print(f"    Overage: {status}")
                print(f"    Type: {overage_type_str}")
                print(f"    Rep Share: {rep_share or 0}%")
                print(f"    Base Commission: {base_rate or 0}%")
                print()

            return {
                "id": str(rows[0][0]),
                "title": rows[0][1],
                "overage_allowed": rows[0][2],
                "overage_type": rows[0][3],
                "rep_overage_share": rows[0][4],
            }

    except Exception as e:
        print(f"Error: {e}")
        return None


def get_products_for_factory(factory_name: str, limit: int = 5) -> list:
    """Get products for a factory."""
    if not DB_AVAILABLE:
        return []

    try:
        db_url = get_database_url()
        engine = create_engine(db_url)

        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT p.id, p.factory_part_number, p.description, p.unit_price, p.default_commission_rate
                    FROM pycore.products p
                    JOIN pycore.factories f ON p.factory_id = f.id
                    WHERE f.title ILIKE :name
                    AND p.unit_price IS NOT NULL
                    AND p.unit_price > 0
                    LIMIT :limit
                """),
                {"name": f"%{factory_name}%", "limit": limit}
            )

            products = []
            for row in result.fetchall():
                products.append({
                    "id": str(row[0]),
                    "partNumber": row[1],
                    "description": row[2],
                    "unitPrice": float(row[3]) if row[3] else 0,
                    "commissionRate": float(row[4]) if row[4] else 0,
                })

            return products

    except Exception as e:
        print(f"Error getting products: {e}")
        return []


# ============================================================================
# API Operations
# ============================================================================

async def get_auth_headers(email: str, password: str) -> dict:
    """Get authentication headers."""
    from tests.common.token_generator import generate_token
    return await generate_token(email=email, password=password)


async def graphql_request(query: str, variables: dict | None, headers: dict) -> dict:
    """Execute a GraphQL request."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            BASE_URL,
            json={"query": query, "variables": variables or {}},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


CREATE_QUOTE_MUTATION = """
mutation CreateQuote($input: QuoteInput!) {
    createQuote(input: $input) {
        id
        quoteNumber
        details {
            id
            productId
            unitPrice
            quantity
            fixtureSchedule
        }
    }
}
"""


async def create_test_quote(
    headers: dict,
    factory_name: str,
) -> dict | None:
    """Create a test quote with overage line items."""

    # Get factory info
    factory_info = check_factory_overage(factory_name)
    if not factory_info:
        return None

    # Get products
    products = get_products_for_factory(factory_name, limit=3)
    if not products:
        print(f"No products found for factory '{factory_name}'")
        return None

    print(f"\nCreating test quote with {len(products)} line items:")
    for p in products:
        print(f"  - {p['partNumber']}: ${p['unitPrice']:.2f}")

    # Build quote input with markup prices (to generate overage)
    fixture_types = ['TYPE_A', 'TYPE_B', 'TYPE_C', 'TYPE_D', 'TYPE_E']
    details = []
    for i, product in enumerate(products):
        base_price = product['unitPrice']
        # Add 20% markup to generate overage
        markup_price = base_price * 1.2

        details.append({
            "productId": product['id'],
            "quantity": 1 + i,
            "unitPrice": str(round(markup_price, 2)),
            "fixtureSchedule": fixture_types[i % len(fixture_types)],
        })

    quote_input = {
        "quoteNumber": f"TEST-OVERAGE-{uuid4().hex[:8].upper()}",
        "entityDate": "2025-01-13",
        "soldToCustomerId": "",  # Will need a valid customer ID
        "status": "OPEN",
        "pipelineStage": "DISCOVERY",
        "details": details,
    }

    print(f"\nQuote number: {quote_input['quoteNumber']}")
    print("\nNote: This requires a valid soldToCustomerId to work.")
    print("Use the frontend to create the quote instead, or update this script with a valid customer ID.")

    return quote_input


# ============================================================================
# Main
# ============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Setup Overage View test data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Enable overage for COOPER LIGHTING LLC
    uv run python tests/overage/setup_overage_test_data.py --enable-overage "COOPER LIGHTING LLC"

    # Check factory overage status
    uv run python tests/overage/setup_overage_test_data.py --check "COOPER LIGHTING"

    # List products for a factory
    uv run python tests/overage/setup_overage_test_data.py --list-products "COOPER LIGHTING"
        """
    )

    parser.add_argument("--enable-overage", metavar="FACTORY", help="Enable overage for factory")
    parser.add_argument("--check", metavar="FACTORY", help="Check factory overage status")
    parser.add_argument("--list-products", metavar="FACTORY", help="List products for factory")
    parser.add_argument("--overage-type", type=int, default=0, choices=[0, 1], help="0=BY_LINE, 1=BY_TOTAL")
    parser.add_argument("--rep-share", type=float, default=100.0, help="Rep overage share percentage (0-100)")
    parser.add_argument("--create-quote", action="store_true", help="Create test quote")
    parser.add_argument("--factory", help="Factory name for quote creation")
    parser.add_argument("--email", "-e", help="User email for API auth")
    parser.add_argument("--password", "-p", help="User password for API auth")
    parser.add_argument("--full-setup", action="store_true", help="Enable overage + create quote")

    args = parser.parse_args()

    if args.enable_overage:
        enable_overage_for_factory(
            args.enable_overage,
            overage_type=args.overage_type,
            rep_share=args.rep_share,
        )

    elif args.check:
        check_factory_overage(args.check)

    elif args.list_products:
        products = get_products_for_factory(args.list_products, limit=10)
        if products:
            print(f"\nProducts for '{args.list_products}':\n")
            for p in products:
                print(f"  {p['partNumber']}: ${p['unitPrice']:.2f} ({p['commissionRate']}% commission)")
                print(f"    {p['description'][:60]}..." if len(p.get('description', '') or '') > 60 else f"    {p.get('description', 'No description')}")
                print()

    elif args.create_quote or args.full_setup:
        if not args.factory:
            print("Error: --factory required for quote creation")
            return

        if args.full_setup:
            enable_overage_for_factory(
                args.factory,
                overage_type=args.overage_type,
                rep_share=args.rep_share,
            )

        if args.email and args.password:
            headers = await get_auth_headers(args.email, args.password)
            await create_test_quote(headers, args.factory)
        else:
            print("\nTo create quote via API, provide --email and --password")
            print("Or use the frontend to create a quote manually.")

    else:
        parser.print_help()
        print("\n" + "=" * 60)
        print("Quick Start:")
        print("=" * 60)
        print("\n1. Check factory status:")
        print('   uv run python tests/overage/setup_overage_test_data.py --check "COOPER LIGHTING"')
        print("\n2. Enable overage:")
        print('   uv run python tests/overage/setup_overage_test_data.py --enable-overage "COOPER LIGHTING LLC"')
        print("\n3. Test in frontend:")
        print("   - Open a quote for COOPER LIGHTING LLC")
        print("   - Switch to Overage View")
        print("   - Verify overage columns show calculated values")


if __name__ == "__main__":
    asyncio.run(main())
