#!/usr/bin/env python3
import argparse
import asyncio
import sys
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
# Frontend Expected Types (from submittals.ts)
# ============================================================================

# Expected enum values that frontend uses
EXPECTED_SUBMITTAL_STATUS = [
    "DRAFT",
    "SUBMITTED",
    "APPROVED",
    "APPROVED_AS_NOTED",
    "REVISE_AND_RESUBMIT",
    "REJECTED",
]
EXPECTED_ITEM_APPROVAL_STATUS = [
    "PENDING",
    "APPROVED",
    "APPROVED_AS_NOTED",
    "REVISE",
    "REJECTED",
]
EXPECTED_ITEM_MATCH_STATUS = ["NO_MATCH", "PARTIAL_MATCH", "EXACT_MATCH"]
EXPECTED_STAKEHOLDER_ROLE = [
    "CUSTOMER",
    "ENGINEER",
    "ARCHITECT",
    "GENERAL_CONTRACTOR",
    "OTHER",
]
EXPECTED_TRANSMITTAL_PURPOSE = [
    "FOR_APPROVAL",
    "FOR_REVIEW",
    "FOR_INFORMATION",
    "FOR_RECORD",
    "RESUBMITTAL",
]


# ============================================================================
# GraphQL Queries that match Frontend
# ============================================================================

# This query matches exactly what the frontend sends (from submittals.ts)
FRONTEND_GET_SUBMITTAL = """
query GetSubmittal($id: UUID!) {
    submittal(id: $id) {
        id
        submittalNumber
        quoteId
        jobId
        status
        transmittalPurpose
        description
        createdAt
        createdBy {
            id
            fullName
        }
        items {
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
            specSheet {
                id
                displayName
                fileUrl
                pageCount
            }
            highlightVersion {
                id
                name
                versionNumber
            }
        }
        stakeholders {
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
        revisions {
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
    }
}
"""

FRONTEND_CREATE_SUBMITTAL = """
mutation CreateSubmittal($input: CreateSubmittalInput!) {
    createSubmittal(input: $input) {
        id
        submittalNumber
        quoteId
        jobId
        status
        transmittalPurpose
        description
        createdAt
        createdBy {
            id
            fullName
        }
        items {
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
        stakeholders {
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
        revisions {
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
    }
}
"""

FRONTEND_GENERATE_PDF = """
mutation GenerateSubmittalPdf($input: GenerateSubmittalPdfInput!) {
    generateSubmittalPdf(input: $input) {
        success
        error
        pdfUrl
        pdfFileName
        pdfFileSizeBytes
        revision {
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
    }
}
"""

DELETE_SUBMITTAL = """
mutation DeleteSubmittal($id: UUID!) {
    deleteSubmittal(id: $id)
}
"""


# ============================================================================
# Contract Verification Functions
# ============================================================================


def verify_submittal_response(submittal: dict) -> list[str]:
    """
    Verify submittal response matches frontend SubmittalResponse interface.

    From submittals.ts:
    interface SubmittalResponse {
        id: string;
        submittalNumber: string;
        quoteId: string | null;
        jobId: string | null;
        status: SubmittalStatusGQL;
        transmittalPurpose: TransmittalPurposeGQL | null;
        description: string | null;
        createdAt: string;
        createdBy: { id: string; fullName: string; };
        items: SubmittalItemResponse[];
        stakeholders: SubmittalStakeholderResponse[];
        revisions: SubmittalRevisionResponse[];
    }
    """
    errors = []

    # Required string fields
    required_strings = ["id", "submittalNumber", "createdAt"]
    for field in required_strings:
        if field not in submittal:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(submittal[field], str):
            errors.append(
                f"Field {field} should be string, got {type(submittal[field]).__name__}"
            )

    # Nullable string fields
    nullable_strings = ["quoteId", "jobId", "description"]
    for field in nullable_strings:
        if field not in submittal:
            errors.append(f"Missing nullable field: {field}")
        elif submittal[field] is not None and not isinstance(submittal[field], str):
            errors.append(
                f"Field {field} should be string or null, got {type(submittal[field]).__name__}"
            )

    # Status enum
    if "status" not in submittal:
        errors.append("Missing required field: status")
    elif submittal["status"] not in EXPECTED_SUBMITTAL_STATUS:
        errors.append(
            f"Invalid status value: {submittal['status']}. Expected one of {EXPECTED_SUBMITTAL_STATUS}"
        )

    # Transmittal purpose enum (nullable)
    if "transmittalPurpose" not in submittal:
        errors.append("Missing nullable field: transmittalPurpose")
    elif (
        submittal["transmittalPurpose"] is not None
        and submittal["transmittalPurpose"] not in EXPECTED_TRANSMITTAL_PURPOSE
    ):
        errors.append(
            f"Invalid transmittalPurpose: {submittal['transmittalPurpose']}. Expected one of {EXPECTED_TRANSMITTAL_PURPOSE}"
        )

    # createdBy object
    if "createdBy" not in submittal:
        errors.append("Missing required field: createdBy")
    elif submittal["createdBy"]:
        created_by = submittal["createdBy"]
        if "id" not in created_by:
            errors.append("createdBy missing field: id")
        if "fullName" not in created_by:
            errors.append("createdBy missing field: fullName")

    # Required arrays
    for field in ["items", "stakeholders", "revisions"]:
        if field not in submittal:
            errors.append(f"Missing required array: {field}")
        elif not isinstance(submittal[field], list):
            errors.append(
                f"Field {field} should be array, got {type(submittal[field]).__name__}"
            )

    # Verify items if present
    if "items" in submittal and isinstance(submittal["items"], list):
        for i, item in enumerate(submittal["items"]):
            item_errors = verify_submittal_item_response(item)
            errors.extend([f"items[{i}].{e}" for e in item_errors])

    # Verify stakeholders if present
    if "stakeholders" in submittal and isinstance(submittal["stakeholders"], list):
        for i, stakeholder in enumerate(submittal["stakeholders"]):
            stakeholder_errors = verify_submittal_stakeholder_response(stakeholder)
            errors.extend([f"stakeholders[{i}].{e}" for e in stakeholder_errors])

    # Verify revisions if present
    if "revisions" in submittal and isinstance(submittal["revisions"], list):
        for i, revision in enumerate(submittal["revisions"]):
            revision_errors = verify_submittal_revision_response(revision)
            errors.extend([f"revisions[{i}].{e}" for e in revision_errors])

    return errors


def verify_submittal_item_response(item: dict) -> list[str]:
    """
    Verify item response matches frontend SubmittalItemResponse interface.

    From submittals.ts:
    interface SubmittalItemResponse {
        id: string;
        submittalId: string;
        itemNumber: number;
        quoteDetailId: string | null;
        specSheetId: string | null;
        highlightVersionId: string | null;
        partNumber: string | null;
        description: string | null;
        quantity: number | null;
        approvalStatus: SubmittalItemApprovalStatusGQL;
        matchStatus: SubmittalItemMatchStatusGQL;
        notes: string | null;
        createdAt: string;
        specSheet: SpecSheetResponse | null;
        highlightVersion: HighlightVersionResponse | null;
    }
    """
    errors = []

    # Required strings
    for field in ["id", "submittalId", "createdAt"]:
        if field not in item:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(item[field], str):
            errors.append(
                f"Field {field} should be string, got {type(item[field]).__name__}"
            )

    # Required number
    if "itemNumber" not in item:
        errors.append("Missing required field: itemNumber")
    elif not isinstance(item["itemNumber"], (int, float)):
        errors.append(
            f"Field itemNumber should be number, got {type(item['itemNumber']).__name__}"
        )

    # Nullable strings
    nullable_strings = [
        "quoteDetailId",
        "specSheetId",
        "highlightVersionId",
        "partNumber",
        "description",
        "notes",
    ]
    for field in nullable_strings:
        if field not in item:
            errors.append(f"Missing nullable field: {field}")

    # Nullable number
    if "quantity" not in item:
        errors.append("Missing nullable field: quantity")

    # Enums
    if "approvalStatus" not in item:
        errors.append("Missing required field: approvalStatus")
    elif item["approvalStatus"] not in EXPECTED_ITEM_APPROVAL_STATUS:
        errors.append(f"Invalid approvalStatus: {item['approvalStatus']}")

    if "matchStatus" not in item:
        errors.append("Missing required field: matchStatus")
    elif item["matchStatus"] not in EXPECTED_ITEM_MATCH_STATUS:
        errors.append(f"Invalid matchStatus: {item['matchStatus']}")

    return errors


def verify_submittal_stakeholder_response(stakeholder: dict) -> list[str]:
    """
    Verify stakeholder response matches frontend SubmittalStakeholderResponse interface.

    From submittals.ts:
    interface SubmittalStakeholderResponse {
        id: string;
        submittalId: string;
        customerId: string | null;
        role: SubmittalStakeholderRoleGQL;
        isPrimary: boolean;
        contactName: string | null;
        contactEmail: string | null;
        contactPhone: string | null;
        companyName: string | null;
    }
    """
    errors = []

    # Required strings
    for field in ["id", "submittalId"]:
        if field not in stakeholder:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(stakeholder[field], str):
            errors.append(f"Field {field} should be string")

    # Required boolean
    if "isPrimary" not in stakeholder:
        errors.append("Missing required field: isPrimary")
    elif not isinstance(stakeholder["isPrimary"], bool):
        errors.append(
            f"Field isPrimary should be boolean, got {type(stakeholder['isPrimary']).__name__}"
        )

    # Role enum
    if "role" not in stakeholder:
        errors.append("Missing required field: role")
    elif stakeholder["role"] not in EXPECTED_STAKEHOLDER_ROLE:
        errors.append(f"Invalid role: {stakeholder['role']}")

    # Nullable strings
    nullable_strings = [
        "customerId",
        "contactName",
        "contactEmail",
        "contactPhone",
        "companyName",
    ]
    for field in nullable_strings:
        if field not in stakeholder:
            errors.append(f"Missing nullable field: {field}")

    return errors


def verify_submittal_revision_response(revision: dict) -> list[str]:
    """
    Verify revision response matches frontend SubmittalRevisionResponse interface.

    From submittals.ts:
    interface SubmittalRevisionResponse {
        id: string;
        submittalId: string;
        revisionNumber: number;
        pdfFileId: string | null;
        pdfFileUrl: string | null;
        pdfFileName: string | null;
        notes: string | null;
        createdAt: string;
        createdBy: { id: string; fullName: string; };
    }
    """
    errors = []

    # Required strings
    for field in ["id", "submittalId", "createdAt"]:
        if field not in revision:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(revision[field], str):
            errors.append(f"Field {field} should be string")

    # Required number
    if "revisionNumber" not in revision:
        errors.append("Missing required field: revisionNumber")
    elif not isinstance(revision["revisionNumber"], (int, float)):
        errors.append(f"Field revisionNumber should be number")

    # Nullable strings
    nullable_strings = ["pdfFileId", "pdfFileUrl", "pdfFileName", "notes"]
    for field in nullable_strings:
        if field not in revision:
            errors.append(f"Missing nullable field: {field}")

    # createdBy object
    if "createdBy" not in revision:
        errors.append("Missing required field: createdBy")
    elif revision["createdBy"]:
        created_by = revision["createdBy"]
        if "id" not in created_by:
            errors.append("createdBy missing field: id")
        if "fullName" not in created_by:
            errors.append("createdBy missing field: fullName")

    return errors


def verify_generate_pdf_response(response: dict) -> list[str]:
    """
    Verify PDF generation response matches frontend GenerateSubmittalPdfResponse interface.

    From submittals.ts:
    interface GenerateSubmittalPdfResponse {
        success: boolean;
        error?: string;
        pdfUrl?: string;
        pdfFileName?: string;
        pdfFileSizeBytes?: number;
        revision?: SubmittalRevisionResponse;
    }
    """
    errors = []

    # Required boolean
    if "success" not in response:
        errors.append("Missing required field: success")
    elif not isinstance(response["success"], bool):
        errors.append(
            f"Field success should be boolean, got {type(response['success']).__name__}"
        )

    # Optional fields (should be present but can be null)
    optional_strings = ["error", "pdfUrl", "pdfFileName"]
    for field in optional_strings:
        if (
            field in response
            and response[field] is not None
            and not isinstance(response[field], str)
        ):
            errors.append(f"Field {field} should be string or null")

    if "pdfFileSizeBytes" in response and response["pdfFileSizeBytes"] is not None:
        if not isinstance(response["pdfFileSizeBytes"], (int, float)):
            errors.append(f"Field pdfFileSizeBytes should be number or null")

    # Revision object (optional)
    if "revision" in response and response["revision"]:
        revision_errors = verify_submittal_revision_response(response["revision"])
        errors.extend([f"revision.{e}" for e in revision_errors])

    return errors


# ============================================================================
# Test Results Tracking
# ============================================================================


class ContractTestResults:
    """Track contract test results."""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: list[str] = []
        self.created_submittal_id: str | None = None

    def pass_test(self, name: str):
        self.passed += 1
        print(f"  ✅ PASSED: {name}")

    def fail_test(self, name: str, errors: list[str]):
        self.failed += 1
        error_str = "; ".join(errors[:5])  # Show first 5 errors
        if len(errors) > 5:
            error_str += f" ... and {len(errors) - 5} more"
        self.errors.append(f"{name}: {error_str}")
        print(f"  ❌ FAILED: {name}")
        for e in errors[:10]:
            print(f"      - {e}")

    def summary(self) -> bool:
        total = self.passed + self.failed
        print(f"\n{'=' * 60}")
        print(f"Contract Test Results: {self.passed}/{total} tests passed")
        if self.failed > 0:
            print("\nFailed tests indicate frontend/backend contract mismatches!")
            print(
                "The frontend expects certain fields/types that the backend doesn't provide."
            )
        print("=" * 60)
        return self.failed == 0


# ============================================================================
# Contract Tests
# ============================================================================


async def test_create_submittal_contract(
    headers: dict, results: ContractTestResults
) -> bool:
    """Test that createSubmittal response matches frontend expectations."""
    test_name = "CreateSubmittal Response Contract"

    submittal_number = f"CONTRACT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    try:
        result = await graphql_request(
            FRONTEND_CREATE_SUBMITTAL,
            variables={
                "input": {
                    "submittalNumber": submittal_number,
                    "status": "DRAFT",
                    "transmittalPurpose": "FOR_APPROVAL",
                    "description": "Contract test submittal",
                }
            },
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, [f"GraphQL error: {result['errors']}"])
            return False

        submittal = result.get("data", {}).get("createSubmittal")
        if not submittal:
            results.fail_test(test_name, ["No submittal returned"])
            return False

        results.created_submittal_id = submittal["id"]

        # Verify contract
        contract_errors = verify_submittal_response(submittal)
        if contract_errors:
            results.fail_test(test_name, contract_errors)
            return False

        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, [str(e)])
        return False


async def test_get_submittal_contract(
    headers: dict, results: ContractTestResults
) -> bool:
    """Test that getSubmittal response matches frontend expectations."""
    test_name = "GetSubmittal Response Contract"

    if not results.created_submittal_id:
        results.fail_test(test_name, ["No submittal ID available"])
        return False

    try:
        result = await graphql_request(
            FRONTEND_GET_SUBMITTAL,
            variables={"id": results.created_submittal_id},
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, [f"GraphQL error: {result['errors']}"])
            return False

        submittal = result.get("data", {}).get("submittal")
        if not submittal:
            results.fail_test(test_name, ["Submittal not found"])
            return False

        # Verify contract
        contract_errors = verify_submittal_response(submittal)
        if contract_errors:
            results.fail_test(test_name, contract_errors)
            return False

        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, [str(e)])
        return False


async def test_generate_pdf_contract(
    headers: dict, results: ContractTestResults
) -> bool:
    """Test that generateSubmittalPdf response matches frontend expectations."""
    test_name = "GenerateSubmittalPdf Response Contract"

    if not results.created_submittal_id:
        results.fail_test(test_name, ["No submittal ID available"])
        return False

    try:
        result = await graphql_request(
            FRONTEND_GENERATE_PDF,
            variables={
                "input": {
                    "submittalId": results.created_submittal_id,
                    "includeCoverPage": True,
                    "includeTransmittalPage": True,
                    "createRevision": True,
                    "revisionNotes": "Contract test revision",
                }
            },
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(test_name, [f"GraphQL error: {result['errors']}"])
            return False

        pdf_response = result.get("data", {}).get("generateSubmittalPdf")
        if not pdf_response:
            results.fail_test(test_name, ["No PDF response returned"])
            return False

        # Verify contract
        contract_errors = verify_generate_pdf_response(pdf_response)
        if contract_errors:
            results.fail_test(test_name, contract_errors)
            return False

        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, [str(e)])
        return False


async def test_input_types_accepted(
    headers: dict, results: ContractTestResults
) -> bool:
    """Test that all frontend input types are accepted by the backend."""
    test_name = "Frontend Input Types Accepted"

    submittal_number = f"INPUT-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Test CreateSubmittalInput with all fields
    create_input = {
        "submittalNumber": submittal_number,
        "status": "DRAFT",
        "transmittalPurpose": "FOR_REVIEW",
        "description": "Test all input fields",
        # These are optional
        # "quoteId": "uuid-here",
        # "jobId": "uuid-here",
    }

    try:
        result = await graphql_request(
            FRONTEND_CREATE_SUBMITTAL,
            variables={"input": create_input},
            headers=headers,
        )

        if "errors" in result:
            results.fail_test(
                test_name, [f"CreateSubmittalInput rejected: {result['errors']}"]
            )
            return False

        submittal = result.get("data", {}).get("createSubmittal")
        if not submittal:
            results.fail_test(test_name, ["No submittal returned"])
            return False

        submittal_id = submittal["id"]

        # Cleanup
        await graphql_request(
            DELETE_SUBMITTAL,
            variables={"id": submittal_id},
            headers=headers,
        )

        results.pass_test(test_name)
        return True

    except Exception as e:
        results.fail_test(test_name, [str(e)])
        return False


async def cleanup_test_submittal(headers: dict, results: ContractTestResults):
    """Clean up the test submittal."""
    if results.created_submittal_id:
        try:
            await graphql_request(
                DELETE_SUBMITTAL,
                variables={"id": results.created_submittal_id},
                headers=headers,
            )
            print(f"\n  🧹 Cleaned up test submittal: {results.created_submittal_id}")
        except Exception as e:
            print(f"\n  ⚠️  Failed to cleanup: {e}")


# ============================================================================
# Main Test Runner
# ============================================================================


async def run_contract_tests(headers: dict) -> bool:
    """Run all frontend contract tests."""
    results = ContractTestResults()

    print("\n" + "=" * 60)
    print("Submittals Frontend Contract Tests")
    print("=" * 60)
    print("\nThese tests verify API responses match frontend TypeScript interfaces.")
    print("Based on: flow-crm/components/lib/graphql/submittals.ts\n")

    # Run contract tests
    print("[1] Testing Response Contracts")
    await test_create_submittal_contract(headers, results)
    await test_get_submittal_contract(headers, results)
    await test_generate_pdf_contract(headers, results)

    print("\n[2] Testing Input Types")
    await test_input_types_accepted(headers, results)

    # Cleanup
    await cleanup_test_submittal(headers, results)

    return results.summary()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Submittals frontend contract tests"
    )
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
