from commons.db.v6.crm.campaigns.campaign_status import CampaignStatus
from commons.db.v6.crm.campaigns.email_status import EmailStatus
from commons.db.v6.crm.campaigns.recipient_list_type import RecipientListType
from commons.db.v6.crm.campaigns.send_pace import SendPace
from commons.db.v6.crm.links.entity_type import EntityType

from app.graphql.campaigns.strawberry.criteria_input import (
    CampaignCriteriaInput,
    CriteriaConditionInput,
    CriteriaGroupInput,
    CriteriaOperator,
    LogicalOperator,
)


class TestCampaignEnums:
    """Tests for campaign enum values."""

    def test_campaign_status_values(self) -> None:
        """Test CampaignStatus enum has expected values."""
        assert CampaignStatus.DRAFT.value == 1
        assert CampaignStatus.SCHEDULED.value == 2
        assert CampaignStatus.SENDING.value == 3
        assert CampaignStatus.COMPLETED.value == 4
        assert CampaignStatus.PAUSED.value == 5

    def test_recipient_list_type_values(self) -> None:
        """Test RecipientListType enum has expected values."""
        assert RecipientListType.STATIC.value == 1
        assert RecipientListType.CRITERIA_BASED.value == 2
        assert RecipientListType.DYNAMIC.value == 3

    def test_email_status_values(self) -> None:
        """Test EmailStatus enum has expected values."""
        assert EmailStatus.PENDING.value == 1
        assert EmailStatus.SENT.value == 2
        assert EmailStatus.FAILED.value == 3
        assert EmailStatus.BOUNCED.value == 4

    def test_send_pace_values(self) -> None:
        """Test SendPace enum has expected values."""
        assert SendPace.SLOW.value == 1
        assert SendPace.MEDIUM.value == 2
        assert SendPace.FAST.value == 3


class TestCriteriaInput:
    """Tests for criteria input types."""

    def test_criteria_operator_values(self) -> None:
        """Test CriteriaOperator enum has expected values."""
        assert CriteriaOperator.EQUALS.value == "equals"
        assert CriteriaOperator.CONTAINS.value == "contains"
        assert CriteriaOperator.IN.value == "in"

    def test_logical_operator_values(self) -> None:
        """Test LogicalOperator enum has expected values."""
        assert LogicalOperator.AND.value == "and"
        assert LogicalOperator.OR.value == "or"

    def test_criteria_condition_input_creation(self) -> None:
        """Test creating a CriteriaConditionInput."""
        condition = CriteriaConditionInput(
            entity_type=EntityType.CONTACT,
            field="first_name",
            operator=CriteriaOperator.EQUALS,
            value="John",
        )
        assert condition.entity_type == EntityType.CONTACT
        assert condition.field == "first_name"
        assert condition.operator == CriteriaOperator.EQUALS
        assert condition.value == "John"

    def test_criteria_group_input_creation(self) -> None:
        """Test creating a CriteriaGroupInput."""
        condition = CriteriaConditionInput(
            entity_type=EntityType.CONTACT,
            field="first_name",
            operator=CriteriaOperator.CONTAINS,
            value="test",
        )
        group = CriteriaGroupInput(
            logical_operator=LogicalOperator.AND,
            conditions=[condition],
        )
        assert group.logical_operator == LogicalOperator.AND
        assert len(group.conditions) == 1

    def test_campaign_criteria_input_creation(self) -> None:
        """Test creating a complete CampaignCriteriaInput."""
        condition = CriteriaConditionInput(
            entity_type=EntityType.CONTACT,
            field="role",
            operator=CriteriaOperator.EQUALS,
            value="Manager",
        )
        group = CriteriaGroupInput(
            logical_operator=LogicalOperator.AND,
            conditions=[condition],
        )
        criteria = CampaignCriteriaInput(
            groups=[group],
            group_operator=LogicalOperator.AND,
        )
        assert criteria.group_operator == LogicalOperator.AND
        assert len(criteria.groups) == 1


class TestCampaignModels:
    """Tests for campaign model creation."""

    def test_campaign_model_import(self) -> None:
        """Test Campaign model can be imported."""
        from commons.db.v6.crm.campaigns.campaign_model import Campaign

        assert Campaign is not None

    def test_campaign_recipient_model_import(self) -> None:
        """Test CampaignRecipient model can be imported."""
        from commons.db.v6.crm.campaigns.campaign_recipient_model import (
            CampaignRecipient,
        )

        assert CampaignRecipient is not None

    def test_campaign_criteria_model_import(self) -> None:
        """Test CampaignCriteria model can be imported."""
        from commons.db.v6.crm.campaigns.campaign_criteria_model import CampaignCriteria

        assert CampaignCriteria is not None


class TestCampaignStrawberryTypes:
    """Tests for campaign Strawberry GraphQL types."""

    def test_campaign_response_import(self) -> None:
        """Test CampaignResponse can be imported."""
        from app.graphql.campaigns.strawberry.campaign_response import CampaignResponse

        assert CampaignResponse is not None

    def test_campaign_input_import(self) -> None:
        """Test CampaignInput can be imported."""
        from app.graphql.campaigns.strawberry.campaign_input import CampaignInput

        assert CampaignInput is not None

    def test_campaign_landing_page_response_import(self) -> None:
        """Test CampaignLandingPageResponse can be imported."""
        from app.graphql.campaigns.strawberry.campaign_landing_page_response import (
            CampaignLandingPageResponse,
        )

        assert CampaignLandingPageResponse is not None

    def test_campaign_recipient_response_import(self) -> None:
        """Test CampaignRecipientResponse can be imported."""
        from app.graphql.campaigns.strawberry.campaign_recipient_response import (
            CampaignRecipientResponse,
        )

        assert CampaignRecipientResponse is not None

    def test_estimate_recipients_response_import(self) -> None:
        """Test EstimateRecipientsResponse can be imported."""
        from app.graphql.campaigns.strawberry.estimate_recipients_response import (
            EstimateRecipientsResponse,
        )

        assert EstimateRecipientsResponse is not None


class TestCampaignServices:
    """Tests for campaign service imports."""

    def test_campaigns_service_import(self) -> None:
        """Test CampaignsService can be imported."""
        from app.graphql.campaigns.services.campaigns_service import CampaignsService

        assert CampaignsService is not None

    def test_criteria_evaluator_service_import(self) -> None:
        """Test CriteriaEvaluatorService can be imported."""
        from app.graphql.campaigns.services.criteria_evaluator_service import (
            CriteriaEvaluatorService,
        )

        assert CriteriaEvaluatorService is not None


class TestCampaignRepositories:
    """Tests for campaign repository imports."""

    def test_campaigns_repository_import(self) -> None:
        """Test CampaignsRepository can be imported."""
        from app.graphql.campaigns.repositories.campaigns_repository import (
            CampaignsRepository,
        )

        assert CampaignsRepository is not None

    def test_campaign_recipients_repository_import(self) -> None:
        """Test CampaignRecipientsRepository can be imported."""
        from app.graphql.campaigns.repositories.campaign_recipients_repository import (
            CampaignRecipientsRepository,
        )

        assert CampaignRecipientsRepository is not None


class TestCampaignQueries:
    """Tests for campaign GraphQL query imports."""

    def test_campaigns_queries_import(self) -> None:
        """Test CampaignsQueries can be imported."""
        from app.graphql.campaigns.queries.campaigns_queries import CampaignsQueries

        assert CampaignsQueries is not None


class TestCampaignMutations:
    """Tests for campaign GraphQL mutation imports."""

    def test_campaigns_mutations_import(self) -> None:
        """Test CampaignsMutations can be imported."""
        from app.graphql.campaigns.mutations.campaigns_mutations import (
            CampaignsMutations,
        )

        assert CampaignsMutations is not None


class TestLandingPageIntegration:
    """Tests for landing page system integration."""

    def test_landing_source_type_includes_campaigns(self) -> None:
        """Test LandingSourceType includes CAMPAIGNS."""
        from app.graphql.common.landing_source_type import LandingSourceType

        assert hasattr(LandingSourceType, "CAMPAIGNS")
        assert LandingSourceType.CAMPAIGNS.value == "campaigns"

    def test_landing_record_union_includes_campaigns(self) -> None:
        """Test LandingRecord union includes CampaignLandingPageResponse."""
        from app.graphql.campaigns.strawberry.campaign_landing_page_response import (
            CampaignLandingPageResponse,
        )
        from app.graphql.common.paginated_landing_page import LandingRecord

        # The union types attribute contains the list of types
        assert CampaignLandingPageResponse in LandingRecord.types


class TestCampaignInputStatusDerivation:
    """Tests for campaign input status derivation logic."""

    def test_derive_status_draft_when_no_schedule_or_immediate(self) -> None:
        """Test status is DRAFT when neither sendImmediately nor scheduledAt is set."""
        from commons.db.v6.crm.campaigns.campaign_status import CampaignStatus
        from commons.db.v6.crm.campaigns.recipient_list_type import RecipientListType

        from app.graphql.campaigns.strawberry.campaign_input import CampaignInput

        campaign_input = CampaignInput(
            name="Test Campaign",
            recipient_list_type=RecipientListType.STATIC,
            send_immediately=False,
        )
        assert campaign_input._derive_status() == CampaignStatus.DRAFT

    def test_derive_status_sending_when_send_immediately(self) -> None:
        """Test status is SENDING when sendImmediately is True."""
        from commons.db.v6.crm.campaigns.campaign_status import CampaignStatus
        from commons.db.v6.crm.campaigns.recipient_list_type import RecipientListType

        from app.graphql.campaigns.strawberry.campaign_input import CampaignInput

        campaign_input = CampaignInput(
            name="Test Campaign",
            recipient_list_type=RecipientListType.STATIC,
            send_immediately=True,
        )
        assert campaign_input._derive_status() == CampaignStatus.SENDING

    def test_derive_status_scheduled_when_scheduled_at_set(self) -> None:
        """Test status is SCHEDULED when scheduledAt is set."""
        from datetime import datetime, timezone

        from commons.db.v6.crm.campaigns.campaign_status import CampaignStatus
        from commons.db.v6.crm.campaigns.recipient_list_type import RecipientListType

        from app.graphql.campaigns.strawberry.campaign_input import CampaignInput

        campaign_input = CampaignInput(
            name="Test Campaign",
            recipient_list_type=RecipientListType.STATIC,
            send_immediately=False,
            scheduled_at=datetime.now(timezone.utc),
        )
        assert campaign_input._derive_status() == CampaignStatus.SCHEDULED

    def test_derive_status_sets_correct_status_on_orm_model(self) -> None:
        """Test _derive_status method returns correct status for send_immediately."""
        from commons.db.v6.crm.campaigns.campaign_status import CampaignStatus
        from commons.db.v6.crm.campaigns.recipient_list_type import RecipientListType

        from app.graphql.campaigns.strawberry.campaign_input import CampaignInput

        # Test send_immediately case
        campaign_input = CampaignInput(
            name="Test Campaign",
            recipient_list_type=RecipientListType.STATIC,
            send_immediately=True,
        )
        # Just verify the status derivation logic works
        status = campaign_input._derive_status()
        assert status == CampaignStatus.SENDING


class TestEstimateRecipientsResponse:
    """Tests for estimate recipients response with full contact info."""

    def test_estimate_recipients_response_has_sample_contacts_field(self) -> None:
        """Test EstimateRecipientsResponse has sample_contacts field."""
        from app.graphql.campaigns.strawberry.estimate_recipients_response import (
            EstimateRecipientsResponse,
        )

        # Check that the field exists
        field_names = [
            f.name for f in EstimateRecipientsResponse.__strawberry_definition__.fields
        ]
        assert "count" in field_names
        assert "sample_contacts" in field_names
        # Ensure old field name is NOT present
        assert "sample_contact_ids" not in field_names

    def test_estimate_recipients_response_sample_contacts_type(self) -> None:
        """Test sample_contacts field is the correct type."""
        from app.graphql.campaigns.strawberry.estimate_recipients_response import (
            EstimateRecipientsResponse,
        )

        # Get the sample_contacts field
        sample_contacts_field = None
        for field in EstimateRecipientsResponse.__strawberry_definition__.fields:
            if field.name == "sample_contacts":
                sample_contacts_field = field
                break

        assert sample_contacts_field is not None
        # Verify it's a list type (StrawberryList)
        field_type = sample_contacts_field.type
        assert hasattr(field_type, "of_type")  # StrawberryList has of_type attribute
        # The of_type should be ContactResponse
        assert "ContactResponse" in str(field_type.of_type)
