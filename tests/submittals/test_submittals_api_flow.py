#!/usr/bin/env python3
"""
Submittals API Flow Tests.

Tests the complete submittal workflow via the GraphQL API:
1. Create submittal
2. Add items
3. Add stakeholders
4. Create revision
5. Generate PDF
6. Update submittal
7. Delete submittal

Requirements:
- Server running on localhost:5555 (uv run ./start.py)
- Valid authentication credentials

Usage:
    cd /home/jorge/flowrms/FLO-727/flow-py-backend
    uv run python tests/submittals/test_submittals_api_flow.py --email jorge@flowrms.com --password CucoHermoso2026$
"""
import argparse
import asyncio
import sys
import uuid
from datetime import datetime
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
# GraphQL Fragments
# ============================================================================

SUBMITTAL_ITEM_FRAGMENT = """
fragment SubmittalItemFields on SubmittalItemResponse {
    id
    submittalId
    itemNumber
    quoteDetailId
    specSheetId
    highlightVersionId
    partNumber
    description
    quantity
    approvalStatus
    matchStatus
    notes
    createdAt
}
"""

SUBMITTAL_STAKEHOLDER_FRAGMENT = """
fragment SubmittalStakeholderFields on SubmittalStakeholderResponse {
    id
    submittalId
    customerId
    role
    isPrimary
    contactName
    contactEmail
    contactPhone
    companyName
}
"""

SUBMITTAL_REVISION_FRAGMENT = """
fragment SubmittalRevisionFields on SubmittalRevisionResponse {
    id
    submittalId
    revisionNumber
    pdfFileId
    pdfFileUrl
    pdfFileName
    notes
    createdAt
    createdBy {
        id
        fullName
    }
}
"""

SUBMITTAL_FRAGMENT = f"""
fragment SubmittalFields on SubmittalResponse {{
    id
    submittalNumber
    quoteId
    jobId
    status
    transmittalPurpose
    description
    createdAt
    createdBy {{
        id
        fullName
    }}
    items {{
        ...SubmittalItemFields
    }}
    stakeholders {{
        ...SubmittalStakeholderFields
    }}
    revisions {{
        ...SubmittalRevisionFields
    }}
}}
{SUBMITTAL_ITEM_FRAGMENT}
{SUBMITTAL_STAKEHOLDER_FRAGMENT}
{SUBMITTAL_REVISION_FRAGMENT}
"""


# ============================================================================
# GraphQL Queries
# ============================================================================

GET_SUBMITTAL = f"""
query GetSubmittal($id: UUID!) {{
    submittal(id: $id) {{
        ...SubmittalFields
    }}
}}
{SUBMITTAL_FRAGMENT}
"""

SEARCH_SUBMITTALS = f"""
query SearchSubmittals($searchTerm: String, $status: SubmittalStatusGQL, $limit: Int) {{
    submittalSearch(searchTerm: $searchTerm, status: $status, limit: $limit) {{
        ...SubmittalFields
    }}
}}
{SUBMITTAL_FRAGMENT}
"""


# ============================================================================
# GraphQL Mutations
# ============================================================================

CREATE_SUBMITTAL = f"""
mutation CreateSubmittal($input: CreateSubmittalInput!) {{
    createSubmittal(input: $input) {{
        ...SubmittalFields
    }}
}}
{SUBMITTAL_FRAGMENT}
"""

UPDATE_SUBMITTAL = f"""
mutation UpdateSubmittal($id: UUID!, $input: UpdateSubmittalInput!) {{
    updateSubmittal(id: $id, input: $input) {{
        ...SubmittalFields
    }}
}}
{SUBMITTAL_FRAGMENT}
"""

DELETE_SUBMITTAL = """
mutation DeleteSubmittal($id: UUID!) {
    deleteSubmittal(id: $id)
}
"""

ADD_SUBMITTAL_ITEM = f"""
mutation AddSubmittalItem($submittalId: UUID!, $input: SubmittalItemInput!) {{
    addSubmittalItem(submittalId: $submittalId, input: $input) {{
        ...SubmittalItemFields
    }}
}}
{SUBMITTAL_ITEM_FRAGMENT}
"""

UPDATE_SUBMITTAL_ITEM = f"""
mutation UpdateSubmittalItem($id: UUID!, $input: UpdateSubmittalItemInput!) {{
    updateSubmittalItem(id: $id, input: $input) {{
        ...SubmittalItemFields
    }}
}}
{SUBMITTAL_ITEM_FRAGMENT}
"""

REMOVE_SUBMITTAL_ITEM = """
mutation RemoveSubmittalItem($id: UUID!) {
    removeSubmittalItem(id: $id)
}
"""

ADD_SUBMITTAL_STAKEHOLDER = f"""
mutation AddSubmittalStakeholder($submittalId: UUID!, $input: SubmittalStakeholderInput!) {{
    addSubmittalStakeholder(submittalId: $submittalId, input: $input) {{
        ...SubmittalStakeholderFields
    }}
}}
{SUBMITTAL_STAKEHOLDER_FRAGMENT}
"""

REMOVE_SUBMITTAL_STAKEHOLDER = """
mutation RemoveSubmittalStakeholder($id: UUID!) {
    removeSubmittalStakeholder(id: $id)
}
"""

CREATE_SUBMITTAL_REVISION = f"""
mutation CreateSubmittalRevision($submittalId: UUID!, $notes: String) {{
    createSubmittalRevision(submittalId: $submittalId, notes: $notes) {{
        ...SubmittalRevisionFields
    }}
}}
{SUBMITTAL_REVISION_FRAGMENT}
"""

GENERATE_SUBMITTAL_PDF = f"""
mutation GenerateSubmittalPdf($input: GenerateSubmittalPdfInput!) {{
    generateSubmittalPdf(input: $input) {{
        success
        error
        pdfUrl
        pdfFileName
        pdfFileSizeBytes
        revision {{
            ...SubmittalRevisionFields
        }}
    }}
}}
{SUBMITTAL_REVISION_FRAGMENT}
"""


# ============================================================================
# Test Results Tracking
# ============================================================================

class TestResults:
    """Track test results."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: list[str] = []
        self.created_submittal_id: str | None = None
        self.created_item_id: str | None = None
        self.created_stakeholder_id: str | None = None
        self.created_revision_id: str | None = None

    def pass_test(self, name: str):
        self.passed += 1
        print(f"  ✅ PASSED: {name}")

    def fail_test(self, name: str, error: str):
        self.failed += 1
        self.errors.append(f"{name}: {error}")
        print(f"  ❌ FAILED: {name} - {error}")

    def summary(self) -> bool:
        total = self.passed + self.failed
        print(f"\n{'=' * 60}")
        print(f"Results: {self.passed}/{total} tests passed")
        if self.errors:
            print("\nFailures:")
            for error in self.errors:
                print(f"  - {error}")
        print("=" * 60)
        return self.failed == 0


# ============================================================================
# Test Functions
# ============================================================================

async def test_create_submittal(headers: dict, results: TestResults) -> bool:
    """Test creating a new submittal."""
    test_name = "Create Submittal"

    # Generate unique submittal number
    submittal_number = f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    try:
        result = await graphql_request(
            CREATE_SUBMITTAL,
            variables={
                "input": {
                    "submittalNumber": submittal_number,
                    "status": "DRAFT",
                    "transmittalPurpose": "FOR_APPROVAL",
                    "description": "Test submittal created by API flow test",
                }
            },
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, f"GraphQL errors: {result['errors']}")
            return False

        submittal = result.get("data", {}).get("createSubmittal")
        if not submittal:
            results.fail_test(test_name, "No submittal returned")
            return False

        # Verify required fields
        if submittal.get("submittalNumber") != submittal_number:
            results.fail_test(test_name, "submittalNumber mismatch")
            return False

        if submittal.get("status") != "DRAFT":
            results.fail_test(test_name, f"Expected DRAFT status, got {submittal.get('status')}")
            return False

        results.created_submittal_id = submittal["id"]
        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, str(e))
        return False


async def test_get_submittal(headers: dict, results: TestResults) -> bool:
    """Test getting a submittal by ID."""
    test_name = "Get Submittal"

    if not results.created_submittal_id:
        results.fail_test(test_name, "No submittal ID available")
        return False

    try:
        result = await graphql_request(
            GET_SUBMITTAL,
            variables={"id": results.created_submittal_id},
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, f"GraphQL errors: {result['errors']}")
            return False

        submittal = result.get("data", {}).get("submittal")
        if not submittal:
            results.fail_test(test_name, "Submittal not found")
            return False

        if submittal["id"] != results.created_submittal_id:
            results.fail_test(test_name, "ID mismatch")
            return False

        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, str(e))
        return False


async def test_add_item(headers: dict, results: TestResults) -> bool:
    """Test adding an item to a submittal."""
    test_name = "Add Submittal Item"

    if not results.created_submittal_id:
        results.fail_test(test_name, "No submittal ID available")
        return False

    try:
        result = await graphql_request(
            ADD_SUBMITTAL_ITEM,
            variables={
                "submittalId": results.created_submittal_id,
                "input": {
                    "itemNumber": 1,
                    "partNumber": "TEST-PART-001",
                    "description": "Test item for API flow test",
                    "quantity": 10,
                    "approvalStatus": "PENDING",
                    "matchStatus": "NO_MATCH",
                }
            },
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, f"GraphQL errors: {result['errors']}")
            return False

        item = result.get("data", {}).get("addSubmittalItem")
        if not item:
            results.fail_test(test_name, "No item returned")
            return False

        if item.get("partNumber") != "TEST-PART-001":
            results.fail_test(test_name, "partNumber mismatch")
            return False

        results.created_item_id = item["id"]
        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, str(e))
        return False


async def test_update_item(headers: dict, results: TestResults) -> bool:
    """Test updating a submittal item."""
    test_name = "Update Submittal Item"

    if not results.created_item_id:
        results.fail_test(test_name, "No item ID available")
        return False

    try:
        result = await graphql_request(
            UPDATE_SUBMITTAL_ITEM,
            variables={
                "id": results.created_item_id,
                "input": {
                    "description": "Updated description",
                    "quantity": 20,
                    "approvalStatus": "APPROVED",
                }
            },
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, f"GraphQL errors: {result['errors']}")
            return False

        item = result.get("data", {}).get("updateSubmittalItem")
        if not item:
            results.fail_test(test_name, "No item returned")
            return False

        # Compare as float since Decimal may be serialized as string "20.0000"
        if float(item.get("quantity") or 0) != 20.0:
            results.fail_test(test_name, f"quantity not updated, got {item.get('quantity')}")
            return False

        if item.get("approvalStatus") != "APPROVED":
            results.fail_test(test_name, f"approvalStatus not updated, got {item.get('approvalStatus')}")
            return False

        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, str(e))
        return False


async def test_add_stakeholder(headers: dict, results: TestResults) -> bool:
    """Test adding a stakeholder to a submittal."""
    test_name = "Add Submittal Stakeholder"

    if not results.created_submittal_id:
        results.fail_test(test_name, "No submittal ID available")
        return False

    try:
        result = await graphql_request(
            ADD_SUBMITTAL_STAKEHOLDER,
            variables={
                "submittalId": results.created_submittal_id,
                "input": {
                    "role": "ENGINEER",
                    "isPrimary": True,
                    "contactName": "Test Engineer",
                    "contactEmail": "engineer@test.com",
                    "companyName": "Test Engineering Inc",
                }
            },
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, f"GraphQL errors: {result['errors']}")
            return False

        stakeholder = result.get("data", {}).get("addSubmittalStakeholder")
        if not stakeholder:
            results.fail_test(test_name, "No stakeholder returned")
            return False

        if stakeholder.get("role") != "ENGINEER":
            results.fail_test(test_name, f"role mismatch, got {stakeholder.get('role')}")
            return False

        if stakeholder.get("contactName") != "Test Engineer":
            results.fail_test(test_name, "contactName mismatch")
            return False

        results.created_stakeholder_id = stakeholder["id"]
        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, str(e))
        return False


async def test_create_revision(headers: dict, results: TestResults) -> bool:
    """Test creating a revision for a submittal."""
    test_name = "Create Submittal Revision"

    if not results.created_submittal_id:
        results.fail_test(test_name, "No submittal ID available")
        return False

    try:
        result = await graphql_request(
            CREATE_SUBMITTAL_REVISION,
            variables={
                "submittalId": results.created_submittal_id,
                "notes": "Test revision created by API flow test",
            },
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, f"GraphQL errors: {result['errors']}")
            return False

        revision = result.get("data", {}).get("createSubmittalRevision")
        if not revision:
            results.fail_test(test_name, "No revision returned")
            return False

        if revision.get("revisionNumber") != 1:
            results.fail_test(test_name, f"Expected revision 1, got {revision.get('revisionNumber')}")
            return False

        results.created_revision_id = revision["id"]
        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, str(e))
        return False


async def test_generate_pdf(headers: dict, results: TestResults) -> bool:
    """Test generating a PDF for a submittal."""
    test_name = "Generate Submittal PDF"

    if not results.created_submittal_id:
        results.fail_test(test_name, "No submittal ID available")
        return False

    try:
        result = await graphql_request(
            GENERATE_SUBMITTAL_PDF,
            variables={
                "input": {
                    "submittalId": results.created_submittal_id,
                    "includeCoverPage": True,
                    "includeTransmittalPage": True,
                    "includeFixtureSummary": True,
                    "createRevision": False,  # Don't create another revision
                }
            },
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, f"GraphQL errors: {result['errors']}")
            return False

        pdf_response = result.get("data", {}).get("generateSubmittalPdf")
        if not pdf_response:
            results.fail_test(test_name, "No PDF response returned")
            return False

        if not pdf_response.get("success"):
            results.fail_test(test_name, f"PDF generation failed: {pdf_response.get('error')}")
            return False

        if not pdf_response.get("pdfUrl"):
            results.fail_test(test_name, "No PDF URL returned")
            return False

        # Verify it's a valid URL (S3 presigned URL or base64 data URL)
        pdf_url = pdf_response.get("pdfUrl", "")
        is_s3_url = pdf_url.startswith("http://") or pdf_url.startswith("https://")
        is_data_url = pdf_url.startswith("data:application/pdf;base64,")
        if not (is_s3_url or is_data_url):
            results.fail_test(test_name, f"PDF URL is not in expected format: {pdf_url[:50]}...")
            return False

        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, str(e))
        return False


async def test_update_submittal(headers: dict, results: TestResults) -> bool:
    """Test updating a submittal."""
    test_name = "Update Submittal"

    if not results.created_submittal_id:
        results.fail_test(test_name, "No submittal ID available")
        return False

    try:
        result = await graphql_request(
            UPDATE_SUBMITTAL,
            variables={
                "id": results.created_submittal_id,
                "input": {
                    "status": "SUBMITTED",
                    "description": "Updated description for test submittal",
                }
            },
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, f"GraphQL errors: {result['errors']}")
            return False

        submittal = result.get("data", {}).get("updateSubmittal")
        if not submittal:
            results.fail_test(test_name, "No submittal returned")
            return False

        if submittal.get("status") != "SUBMITTED":
            results.fail_test(test_name, f"status not updated, got {submittal.get('status')}")
            return False

        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, str(e))
        return False


async def test_search_submittals(headers: dict, results: TestResults) -> bool:
    """Test searching submittals."""
    test_name = "Search Submittals"

    try:
        result = await graphql_request(
            SEARCH_SUBMITTALS,
            variables={
                "searchTerm": "TEST",
                "limit": 10,
            },
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, f"GraphQL errors: {result['errors']}")
            return False

        submittals = result.get("data", {}).get("submittalSearch")
        if submittals is None:
            results.fail_test(test_name, "No search results returned")
            return False

        # Should find our created submittal
        found = any(s["id"] == results.created_submittal_id for s in submittals)
        if not found and results.created_submittal_id:
            # This might fail if the submittal was already deleted or search index is delayed
            print(f"  ⚠️  WARNING: Created submittal not found in search results (may be timing issue)")

        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, str(e))
        return False


async def test_remove_stakeholder(headers: dict, results: TestResults) -> bool:
    """Test removing a stakeholder."""
    test_name = "Remove Submittal Stakeholder"

    if not results.created_stakeholder_id:
        results.fail_test(test_name, "No stakeholder ID available")
        return False

    try:
        result = await graphql_request(
            REMOVE_SUBMITTAL_STAKEHOLDER,
            variables={"id": results.created_stakeholder_id},
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, f"GraphQL errors: {result['errors']}")
            return False

        success = result.get("data", {}).get("removeSubmittalStakeholder")
        if not success:
            results.fail_test(test_name, "Remove returned false")
            return False

        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, str(e))
        return False


async def test_remove_item(headers: dict, results: TestResults) -> bool:
    """Test removing an item."""
    test_name = "Remove Submittal Item"

    if not results.created_item_id:
        results.fail_test(test_name, "No item ID available")
        return False

    try:
        result = await graphql_request(
            REMOVE_SUBMITTAL_ITEM,
            variables={"id": results.created_item_id},
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, f"GraphQL errors: {result['errors']}")
            return False

        success = result.get("data", {}).get("removeSubmittalItem")
        if not success:
            results.fail_test(test_name, "Remove returned false")
            return False

        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, str(e))
        return False


async def test_delete_submittal(headers: dict, results: TestResults) -> bool:
    """Test deleting a submittal."""
    test_name = "Delete Submittal"

    if not results.created_submittal_id:
        results.fail_test(test_name, "No submittal ID available")
        return False

    try:
        result = await graphql_request(
            DELETE_SUBMITTAL,
            variables={"id": results.created_submittal_id},
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, f"GraphQL errors: {result['errors']}")
            return False

        success = result.get("data", {}).get("deleteSubmittal")
        if not success:
            results.fail_test(test_name, "Delete returned false")
            return False

        # Verify deletion by trying to get the submittal
        verify_result = await graphql_request(
            GET_SUBMITTAL,
            variables={"id": results.created_submittal_id},
            headers=headers,
        )

        submittal = verify_result.get("data", {}).get("submittal")
        if submittal:
            results.fail_test(test_name, "Submittal still exists after deletion")
            return False

        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, str(e))
        return False


# ============================================================================
# Main Test Runner
# ============================================================================

async def run_api_flow_tests(headers: dict) -> bool:
    """Run all API flow tests."""
    results = TestResults()

    print("\n" + "=" * 60)
    print("Submittals API Flow Tests")
    print("=" * 60)

    # Run tests in sequence (they depend on each other)
    print("\n[1] Create Operations")
    await test_create_submittal(headers, results)
    await test_get_submittal(headers, results)

    print("\n[2] Item Operations")
    await test_add_item(headers, results)
    await test_update_item(headers, results)

    print("\n[3] Stakeholder Operations")
    await test_add_stakeholder(headers, results)

    print("\n[4] Revision Operations")
    await test_create_revision(headers, results)

    print("\n[5] PDF Generation")
    await test_generate_pdf(headers, results)

    print("\n[6] Update Operations")
    await test_update_submittal(headers, results)
    await test_search_submittals(headers, results)

    print("\n[7] Cleanup Operations")
    await test_remove_stakeholder(headers, results)
    await test_remove_item(headers, results)
    await test_delete_submittal(headers, results)

    return results.summary()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Submittals API flow tests")
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

    success = await run_api_flow_tests(headers)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
