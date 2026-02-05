#!/usr/bin/env python3
import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

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
# GraphQL Queries for Contract Testing
# ============================================================================

GET_SPEC_SHEETS_BY_FACTORY = """
query GetSpecSheetsByFactory($factoryId: UUID!, $publishedOnly: Boolean) {
    specSheetsByFactory(factoryId: $factoryId, publishedOnly: $publishedOnly) {
        id
        factoryId
        fileName
        displayName
        uploadSource
        sourceUrl
        fileUrl
        fileSize
        pageCount
        categories
        tags
        folderPath
        needsReview
        published
        usageCount
        highlightCount
        createdAt
        createdBy {
            id
            email
            firstName
            lastName
            fullName
        }
    }
}
"""

GET_HIGHLIGHT_VERSIONS = """
query GetHighlightVersions($specSheetId: UUID!) {
    specSheetHighlightVersions(specSheetId: $specSheetId) {
        id
        specSheetId
        name
        description
        versionNumber
        isActive
        regions {
            id
            pageNumber
            x
            y
            width
            height
            shapeType
            color
            annotation
            createdAt
        }
        createdAt
        createdBy {
            id
            fullName
        }
    }
}
"""

GET_FACTORIES = """
query GetFactories {
    factories(limit: 10) {
        items {
            id
            title
        }
    }
}
"""


# ============================================================================
# Contract Verification Functions
# ============================================================================


def verify_spec_sheet_response(spec_sheet: dict) -> list[str]:
    """Verify spec sheet response has all fields frontend expects."""
    errors = []

    # Required string fields
    required_strings = [
        "id",
        "factoryId",
        "fileName",
        "displayName",
        "uploadSource",
        "fileUrl",
        "createdAt",
    ]
    for field in required_strings:
        if field not in spec_sheet:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(spec_sheet[field], str):
            errors.append(
                f"Field {field} should be string, got {type(spec_sheet[field])}"
            )

    # Required numeric fields
    required_numbers = ["fileSize", "pageCount", "usageCount", "highlightCount"]
    for field in required_numbers:
        if field not in spec_sheet:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(spec_sheet[field], (int, float)):
            errors.append(
                f"Field {field} should be number, got {type(spec_sheet[field])}"
            )

    # Required boolean fields
    required_bools = ["needsReview", "published"]
    for field in required_bools:
        if field not in spec_sheet:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(spec_sheet[field], bool):
            errors.append(
                f"Field {field} should be boolean, got {type(spec_sheet[field])}"
            )

    # Required array fields
    required_arrays = ["categories"]
    for field in required_arrays:
        if field not in spec_sheet:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(spec_sheet[field], list):
            errors.append(
                f"Field {field} should be array, got {type(spec_sheet[field])}"
            )

    # Nullable fields (should exist but can be null)
    nullable_fields = ["sourceUrl", "tags", "folderPath"]
    for field in nullable_fields:
        if field not in spec_sheet:
            errors.append(f"Missing nullable field: {field}")

    # createdBy object
    if "createdBy" not in spec_sheet:
        errors.append("Missing createdBy object")
    elif spec_sheet["createdBy"]:
        created_by = spec_sheet["createdBy"]
        for field in ["id", "fullName"]:
            if field not in created_by:
                errors.append(f"createdBy missing field: {field}")

    return errors


def verify_highlight_version_response(version: dict) -> list[str]:
    """Verify highlight version response has all fields frontend expects."""
    errors = []

    # Required fields
    required_fields = [
        "id",
        "specSheetId",
        "name",
        "versionNumber",
        "isActive",
        "createdAt",
    ]
    for field in required_fields:
        if field not in version:
            errors.append(f"Missing required field: {field}")

    # regions array
    if "regions" not in version:
        errors.append("Missing regions array")
    elif version["regions"]:
        for i, region in enumerate(version["regions"]):
            # Verify region has required fields
            region_fields = [
                "id",
                "pageNumber",
                "x",
                "y",
                "width",
                "height",
                "shapeType",
                "color",
            ]
            for field in region_fields:
                if field not in region:
                    errors.append(f"Region {i} missing field: {field}")

            # Verify shapeType is valid
            valid_shapes = [
                "highlight",
                "rectangle",
                "circle",
                "arrow",
                "text",
                "freehand",
            ]
            if (
                "shapeType" in region
                and region["shapeType"].lower() not in valid_shapes
            ):
                errors.append(
                    f"Region {i} has invalid shapeType: {region['shapeType']}"
                )

    # createdBy object
    if "createdBy" not in version:
        errors.append("Missing createdBy object")
    elif version["createdBy"]:
        if "fullName" not in version["createdBy"]:
            errors.append("createdBy missing fullName")

    return errors


def verify_factory_response(factory: dict) -> list[str]:
    """Verify factory response has fields frontend expects."""
    errors = []

    # Frontend expects id and title (mapped to name)
    if "id" not in factory:
        errors.append("Missing id field")
    if "title" not in factory:
        errors.append("Missing title field (frontend maps this to 'name')")

    return errors


# ============================================================================
# Main Test Runner
# ============================================================================


async def run_contract_tests(headers: dict) -> bool:
    """Run all contract tests and return success status."""
    all_passed = True

    print("\n" + "=" * 60)
    print("API Contract Tests")
    print("=" * 60)

    # Test 1: Get Factories (to get a factory ID for other tests)
    print("\n[1] Testing GET_FACTORIES...")
    try:
        result = await graphql_request(GET_FACTORIES, headers=headers)
        if "errors" in result:
            print(f"  FAILED: GraphQL errors: {result['errors']}")
            all_passed = False
        elif not result.get("data", {}).get("factories", {}).get("items"):
            print("  SKIPPED: No factories found")
        else:
            factories = result["data"]["factories"]["items"]
            for factory in factories[:3]:  # Test first 3
                errors = verify_factory_response(factory)
                if errors:
                    print(f"  FAILED: Factory {factory.get('id')}: {errors}")
                    all_passed = False
            print(f"  PASSED: Verified {len(factories)} factory responses")
    except Exception as e:
        print(f"  ERROR: {e}")
        all_passed = False

    # Test 2: Get Spec Sheets (if we have a factory)
    print("\n[2] Testing GET_SPEC_SHEETS_BY_FACTORY...")
    try:
        result = await graphql_request(GET_FACTORIES, headers=headers)
        factories = result.get("data", {}).get("factories", {}).get("items", [])
        if not factories:
            print("  SKIPPED: No factories available")
        else:
            factory_id = factories[0]["id"]
            result = await graphql_request(
                GET_SPEC_SHEETS_BY_FACTORY,
                variables={"factoryId": factory_id, "publishedOnly": False},
                headers=headers,
            )
            if "errors" in result:
                print(f"  FAILED: GraphQL errors: {result['errors']}")
                all_passed = False
            else:
                spec_sheets = result.get("data", {}).get("specSheetsByFactory", [])
                if not spec_sheets:
                    print(f"  SKIPPED: No spec sheets for factory {factory_id}")
                else:
                    for sheet in spec_sheets[:3]:
                        errors = verify_spec_sheet_response(sheet)
                        if errors:
                            print(f"  FAILED: Spec sheet {sheet.get('id')}: {errors}")
                            all_passed = False
                    print(f"  PASSED: Verified {len(spec_sheets)} spec sheet responses")
    except Exception as e:
        print(f"  ERROR: {e}")
        all_passed = False

    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL CONTRACT TESTS PASSED")
    else:
        print("SOME CONTRACT TESTS FAILED")
    print("=" * 60)

    return all_passed


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run API contract tests")
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
    except Exception as e:
        print(f"Failed to generate token: {e}")
        sys.exit(1)

    success = await run_contract_tests(headers)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
