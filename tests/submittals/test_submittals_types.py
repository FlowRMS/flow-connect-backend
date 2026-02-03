#!/usr/bin/env python3
"""
Unit tests for Submittals GraphQL types and enums.
Tests data structures and transformations without requiring a running server.

These tests verify:
1. Enum values match between frontend and backend
2. Response types have all required fields
3. Input types validate correctly

NOTE: These tests require flowbot-commons with submittals module.
In local development, update pyproject.toml to use local flowbot-commons:
  flowbot-commons = { path = "../flowbot-commons" }
Then run: uv sync
"""
import pytest
from decimal import Decimal
from uuid import UUID, uuid4

# Check if submittals module is available
try:
    from commons.db.v6.crm.submittals import Submittal
    SUBMITTALS_AVAILABLE = True
except ImportError:
    SUBMITTALS_AVAILABLE = False

# Skip all tests if submittals module not available
pytestmark = pytest.mark.skipif(
    not SUBMITTALS_AVAILABLE,
    reason="Submittals module not available. Update pyproject.toml to use local flowbot-commons."
)


# ============================================================================
# Test Enum Values Match Frontend Expectations
# ============================================================================

class TestSubmittalEnums:
    """Test that enum values match what the frontend expects."""

    def test_submittal_status_values(self):
        """Verify SubmittalStatus enum values match frontend expectations."""
        from commons.db.v6.crm.submittals import SubmittalStatus

        # Frontend expects these exact values
        expected_values = {
            'DRAFT': 0,
            'SUBMITTED': 1,
            'APPROVED': 2,
            'APPROVED_AS_NOTED': 3,
            'REVISE_AND_RESUBMIT': 4,
            'REJECTED': 5,
        }

        for name, value in expected_values.items():
            assert hasattr(SubmittalStatus, name), f"Missing status: {name}"
            assert SubmittalStatus[name].value == value, f"Wrong value for {name}"

    def test_submittal_item_approval_status_values(self):
        """Verify SubmittalItemApprovalStatus enum values match frontend."""
        from commons.db.v6.crm.submittals import SubmittalItemApprovalStatus

        expected_values = {
            'PENDING': 0,
            'APPROVED': 1,
            'APPROVED_AS_NOTED': 2,
            'REVISE': 3,
            'REJECTED': 4,
        }

        for name, value in expected_values.items():
            assert hasattr(SubmittalItemApprovalStatus, name), f"Missing status: {name}"
            assert SubmittalItemApprovalStatus[name].value == value, f"Wrong value for {name}"

    def test_submittal_item_match_status_values(self):
        """Verify SubmittalItemMatchStatus enum values match frontend."""
        from commons.db.v6.crm.submittals import SubmittalItemMatchStatus

        expected_values = {
            'NO_MATCH': 0,
            'PARTIAL_MATCH': 1,
            'EXACT_MATCH': 2,
        }

        for name, value in expected_values.items():
            assert hasattr(SubmittalItemMatchStatus, name), f"Missing status: {name}"
            assert SubmittalItemMatchStatus[name].value == value, f"Wrong value for {name}"

    def test_submittal_stakeholder_role_values(self):
        """Verify SubmittalStakeholderRole enum values match frontend."""
        from commons.db.v6.crm.submittals import SubmittalStakeholderRole

        expected_values = {
            'CUSTOMER': 0,
            'ENGINEER': 1,
            'ARCHITECT': 2,
            'GENERAL_CONTRACTOR': 3,
            'OTHER': 4,
        }

        for name, value in expected_values.items():
            assert hasattr(SubmittalStakeholderRole, name), f"Missing role: {name}"
            assert SubmittalStakeholderRole[name].value == value, f"Wrong value for {name}"

    def test_transmittal_purpose_values(self):
        """Verify TransmittalPurpose enum values match frontend."""
        from commons.db.v6.crm.submittals import TransmittalPurpose

        expected_values = {
            'FOR_APPROVAL': 0,
            'FOR_REVIEW': 1,
            'FOR_INFORMATION': 2,
            'FOR_RECORD': 3,
            'RESUBMITTAL': 4,
        }

        for name, value in expected_values.items():
            assert hasattr(TransmittalPurpose, name), f"Missing purpose: {name}"
            assert TransmittalPurpose[name].value == value, f"Wrong value for {name}"


# ============================================================================
# Test Model Field Types
# ============================================================================

class TestSubmittalModels:
    """Test that model fields have correct types for API serialization."""

    def test_submittal_model_has_required_fields(self):
        """Verify Submittal model has all fields expected by frontend."""
        from commons.db.v6.crm.submittals import Submittal

        # Fields the frontend expects
        required_fields = [
            'id',
            'submittal_number',
            'quote_id',
            'job_id',
            'status',
            'transmittal_purpose',
            'description',
            'created_at',
            # Relationships
            'items',
            'stakeholders',
            'revisions',
        ]

        for field in required_fields:
            assert hasattr(Submittal, field), f"Missing field: {field}"

    def test_submittal_item_model_has_required_fields(self):
        """Verify SubmittalItem model has all fields expected by frontend."""
        from commons.db.v6.crm.submittals import SubmittalItem

        required_fields = [
            'id',
            'item_number',
            'quote_detail_id',
            'spec_sheet_id',
            'highlight_version_id',
            'part_number',
            'description',
            'quantity',
            'approval_status',
            'match_status',
            'notes',
            'created_at',
        ]

        for field in required_fields:
            assert hasattr(SubmittalItem, field), f"Missing field: {field}"

    def test_submittal_stakeholder_model_has_required_fields(self):
        """Verify SubmittalStakeholder model has all fields expected by frontend."""
        from commons.db.v6.crm.submittals import SubmittalStakeholder

        required_fields = [
            'id',
            'role',
            'customer_id',
            'is_primary',
            'contact_name',
            'contact_email',
            'contact_phone',
            'company_name',
        ]

        for field in required_fields:
            assert hasattr(SubmittalStakeholder, field), f"Missing field: {field}"

    def test_submittal_revision_model_has_required_fields(self):
        """Verify SubmittalRevision model has all fields expected by frontend."""
        from commons.db.v6.crm.submittals import SubmittalRevision

        required_fields = [
            'id',
            'revision_number',
            'pdf_file_id',
            'pdf_file_url',
            'pdf_file_name',
            'notes',
            'created_at',
        ]

        for field in required_fields:
            assert hasattr(SubmittalRevision, field), f"Missing field: {field}"


# ============================================================================
# Test Spec Sheet Highlight Types
# ============================================================================

class TestSpecSheetHighlightTypes:
    """Test spec sheet highlight related types for frontend compatibility."""

    def test_highlight_region_model_has_required_fields(self):
        """Verify SpecSheetHighlightRegion has fields expected by frontend."""
        from commons.db.v6.crm.spec_sheets import SpecSheetHighlightRegion

        # Fields the frontend expects for rendering highlights
        required_fields = [
            'id',
            'page_number',
            'x',
            'y',
            'width',
            'height',
            'shape_type',
            'color',
            'annotation',
            'created_at',
        ]

        for field in required_fields:
            assert hasattr(SpecSheetHighlightRegion, field), f"Missing field: {field}"

    def test_highlight_version_model_has_required_fields(self):
        """Verify SpecSheetHighlightVersion has fields expected by frontend."""
        from commons.db.v6.crm.spec_sheets import SpecSheetHighlightVersion

        required_fields = [
            'id',
            'spec_sheet_id',
            'name',
            'description',
            'version_number',
            'is_active',
            'created_at',
            # Relationship
            'regions',
        ]

        for field in required_fields:
            assert hasattr(SpecSheetHighlightVersion, field), f"Missing field: {field}"


# ============================================================================
# Test Quote Detail Overage Fields
# ============================================================================

class TestQuoteDetailOverageFields:
    """Test overage fields added to QuoteDetail for Overage View feature."""

    def test_quote_detail_has_overage_fields(self):
        """Verify QuoteDetail has overage fields expected by frontend."""
        from commons.db.v6.crm.quotes import QuoteDetail

        # Fields added for Overage View feature
        overage_fields = [
            'overage_commission_rate',
            'overage_commission',
            'overage_unit_price',
            'fixture_schedule',
        ]

        for field in overage_fields:
            assert hasattr(QuoteDetail, field), f"Missing overage field: {field}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
