#!/usr/bin/env python3
"""
Token generator for product category hierarchy tests.
Generates authentication tokens for API testing.

Usage:
    uv run python tests/products/token_generator.py --email your@email.com --password yourpassword
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.auth.workos_auth_service import WorkOSAuthService
from app.core.config.base_settings import get_settings_local
from app.core.config.workos_settings import WorkOSSettings


async def generate_token(
    email: str,
    password: str,
    organization_id: str | None = None,
) -> dict[str, str]:
    """Generate authentication headers for API requests."""
    auth_service = WorkOSAuthService(
        workos_settings=get_settings_local(env="prod", cls=WorkOSSettings)
    )

    token = await auth_service.authenticate(
        email=email, password=password, tenant_id=organization_id
    )
    if not token:
        raise ValueError("Failed to generate token")

    return {
        "Authorization": f"Bearer {token.access_token}",
        "X-Auth-Provider": "WORKOS",
        "Content-Type": "application/json",
    }


async def main():
    """Generate and print token headers."""
    parser = argparse.ArgumentParser(description="Generate authentication token")
    parser.add_argument("--email", "-e", required=True, help="User email")
    parser.add_argument("--password", "-p", required=True, help="User password")
    parser.add_argument("--org-id", "-o", help="Organization ID (optional)")

    args = parser.parse_args()

    print(f"Generating token for: {args.email}")

    try:
        headers = await generate_token(
            email=args.email,
            password=args.password,
            organization_id=args.org_id,
        )
        print(json.dumps(headers, indent=2))
        return headers
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
