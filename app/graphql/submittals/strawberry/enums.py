"""GraphQL enum types for Submittals."""

from enum import Enum

import strawberry
from commons.db.v6.crm.submittals import (
    SubmittalItemApprovalStatus,
    SubmittalItemMatchStatus,
    SubmittalStakeholderRole,
    SubmittalStatus,
    TransmittalPurpose,
)


@strawberry.enum
class SubmittalStatusGQL(Enum):
    """GraphQL enum for submittal status."""

    DRAFT = SubmittalStatus.DRAFT.value
    SUBMITTED = SubmittalStatus.SUBMITTED.value
    APPROVED = SubmittalStatus.APPROVED.value
    APPROVED_AS_NOTED = SubmittalStatus.APPROVED_AS_NOTED.value
    REVISE_AND_RESUBMIT = SubmittalStatus.REVISE_AND_RESUBMIT.value
    REJECTED = SubmittalStatus.REJECTED.value


@strawberry.enum
class SubmittalItemApprovalStatusGQL(Enum):
    """GraphQL enum for submittal item approval status."""

    PENDING = SubmittalItemApprovalStatus.PENDING.value
    APPROVED = SubmittalItemApprovalStatus.APPROVED.value
    APPROVED_AS_NOTED = SubmittalItemApprovalStatus.APPROVED_AS_NOTED.value
    REVISE = SubmittalItemApprovalStatus.REVISE.value
    REJECTED = SubmittalItemApprovalStatus.REJECTED.value


@strawberry.enum
class SubmittalItemMatchStatusGQL(Enum):
    """GraphQL enum for submittal item match status."""

    NO_MATCH = SubmittalItemMatchStatus.NO_MATCH.value
    PARTIAL_MATCH = SubmittalItemMatchStatus.PARTIAL_MATCH.value
    EXACT_MATCH = SubmittalItemMatchStatus.EXACT_MATCH.value


@strawberry.enum
class SubmittalStakeholderRoleGQL(Enum):
    """GraphQL enum for stakeholder roles."""

    CUSTOMER = SubmittalStakeholderRole.CUSTOMER.value
    ENGINEER = SubmittalStakeholderRole.ENGINEER.value
    ARCHITECT = SubmittalStakeholderRole.ARCHITECT.value
    GENERAL_CONTRACTOR = SubmittalStakeholderRole.GENERAL_CONTRACTOR.value
    OTHER = SubmittalStakeholderRole.OTHER.value


@strawberry.enum
class TransmittalPurposeGQL(Enum):
    """GraphQL enum for transmittal purpose."""

    FOR_APPROVAL = TransmittalPurpose.FOR_APPROVAL.value
    FOR_REVIEW = TransmittalPurpose.FOR_REVIEW.value
    FOR_INFORMATION = TransmittalPurpose.FOR_INFORMATION.value
    FOR_RECORD = TransmittalPurpose.FOR_RECORD.value
    RESUBMITTAL = TransmittalPurpose.RESUBMITTAL.value
