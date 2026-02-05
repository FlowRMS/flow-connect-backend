from typing import Any
from uuid import UUID

import strawberry
from commons.auth import AuthInfo
from commons.db.v6.crm.campaigns.campaign_criteria_model import CampaignCriteria
from commons.db.v6.crm.campaigns.campaign_model import Campaign
from commons.db.v6.crm.campaigns.campaign_recipient_model import CampaignRecipient
from commons.db.v6.crm.campaigns.campaign_status import CampaignStatus
from commons.db.v6.crm.campaigns.email_status import EmailStatus
from commons.db.v6.crm.campaigns.recipient_list_type import RecipientListType
from commons.db.v6.crm.contact_model import Contact
from commons.db.v6.crm.links.entity_type import EntityType

from app.errors.common_errors import NotFoundError
from app.graphql.campaigns.repositories.campaign_recipients_repository import (
    CampaignRecipientsRepository,
)
from app.graphql.campaigns.repositories.campaigns_repository import CampaignsRepository
from app.graphql.campaigns.services.criteria_evaluator_service import (
    CriteriaEvaluatorService,
)
from app.graphql.campaigns.services.email_provider_service import EmailProviderService
from app.graphql.campaigns.strawberry.campaign_input import CampaignInput
from app.graphql.campaigns.strawberry.criteria_input import (
    CampaignCriteriaInput,
    CriteriaConditionInput,
    CriteriaGroupInput,
    CriteriaOperator,
    LogicalOperator,
)


class NoEmailProviderError(Exception):
    """Raised when user has no email provider connected."""

    def __init__(self) -> None:
        super().__init__(
            "No email provider connected. Please connect O365 or Gmail before creating a campaign."
        )


class CampaignsService:
    """Service for Campaigns entity business logic."""

    def __init__(
        self,
        repository: CampaignsRepository,
        recipients_repository: CampaignRecipientsRepository,
        criteria_evaluator: CriteriaEvaluatorService,
        email_provider: EmailProviderService,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.repository = repository
        self.recipients_repository = recipients_repository
        self.criteria_evaluator = criteria_evaluator
        self.email_provider = email_provider
        self.auth_info = auth_info

    async def create_campaign(self, campaign_input: CampaignInput) -> Campaign:
        """Create a new campaign with recipients.

        Raises:
            NoEmailProviderError: If user has no O365 or Gmail connected.
        """
        # Check if user has email provider connected
        if not await self.email_provider.has_connected_provider():
            raise NoEmailProviderError()

        campaign = await self.repository.create(campaign_input.to_orm_model())

        match campaign_input.recipient_list_type:
            case RecipientListType.STATIC:
                await self._add_static_recipients(
                    campaign.id, campaign_input.static_contact_ids
                )
            case RecipientListType.CRITERIA_BASED:
                await self._add_criteria_based_recipients(
                    campaign.id, campaign_input.criteria, is_dynamic=False
                )
            case RecipientListType.DYNAMIC:
                await self._add_criteria_based_recipients(
                    campaign.id, campaign_input.criteria, is_dynamic=True
                )

        result = await self.repository.get_with_relations(campaign.id)
        if not result:
            raise NotFoundError(str(campaign.id))
        return result

    async def _add_static_recipients(
        self,
        campaign_id: UUID,
        contact_ids: list[UUID] | None,
    ) -> None:
        """Add static list of contacts as recipients."""
        if not contact_ids or contact_ids == strawberry.UNSET:
            return

        recipients = [
            CampaignRecipient(
                campaign_id=campaign_id,
                contact_id=contact_id,
                email_status=EmailStatus.PENDING,
            )
            for contact_id in contact_ids
        ]
        _ = await self.recipients_repository.bulk_create(recipients)

    async def _add_criteria_based_recipients(
        self,
        campaign_id: UUID,
        criteria: CampaignCriteriaInput | None,
        is_dynamic: bool,
    ) -> None:
        """Add recipients based on criteria evaluation."""
        if not criteria or criteria == strawberry.UNSET:
            return

        criteria_model = CampaignCriteria(
            campaign_id=campaign_id,
            criteria_json=self._criteria_to_dict(criteria),
            is_dynamic=is_dynamic,
        )
        self.repository.session.add(criteria_model)

        contacts = await self.criteria_evaluator.evaluate_criteria(criteria)

        recipients = [
            CampaignRecipient(
                campaign_id=campaign_id,
                contact_id=contact.id,
                email_status=EmailStatus.PENDING,
            )
            for contact in contacts
        ]
        if recipients:
            _ = await self.recipients_repository.bulk_create(recipients)

    def _criteria_to_dict(self, criteria: CampaignCriteriaInput) -> dict[str, Any]:
        """Convert criteria input to JSON-serializable dict."""
        return {
            "group_operator": criteria.group_operator.value,
            "groups": [
                {
                    "logical_operator": group.logical_operator.value,
                    "conditions": [
                        {
                            "entity_type": cond.entity_type.value,
                            "field": cond.field,
                            "operator": cond.operator.value,
                            "value": cond.value,
                        }
                        for cond in group.conditions
                    ],
                }
                for group in criteria.groups
            ],
        }

    async def get_campaign(self, campaign_id: UUID) -> Campaign:
        """Get a campaign by ID with relations."""
        campaign = await self.repository.get_with_relations(campaign_id)
        if not campaign:
            raise NotFoundError(str(campaign_id))
        return campaign

    async def update_campaign(
        self,
        campaign_id: UUID,
        campaign_input: CampaignInput,
    ) -> Campaign:
        """Update an existing campaign."""
        if not await self.repository.exists(campaign_id):
            raise NotFoundError(str(campaign_id))

        campaign = campaign_input.to_orm_model()
        campaign.id = campaign_id
        updated = await self.repository.update(campaign)
        result = await self.repository.get_with_relations(updated.id)
        if not result:
            raise NotFoundError(str(updated.id))
        return result

    async def delete_campaign(self, campaign_id: UUID) -> bool:
        """Delete a campaign and all its recipients."""
        if not await self.repository.exists(campaign_id):
            raise NotFoundError(str(campaign_id))
        return await self.repository.delete(campaign_id)

    async def pause_campaign(self, campaign_id: UUID) -> Campaign:
        """Pause a sending campaign."""
        campaign = await self.repository.get_by_id(campaign_id)
        if not campaign:
            raise NotFoundError(str(campaign_id))

        campaign.status = CampaignStatus.PAUSED
        await self.repository.session.flush()
        result = await self.repository.get_with_relations(campaign_id)
        if not result:
            raise NotFoundError(str(campaign_id))
        return result

    async def resume_campaign(self, campaign_id: UUID) -> Campaign:
        """Resume a paused campaign."""
        campaign = await self.repository.get_by_id(campaign_id)
        if not campaign:
            raise NotFoundError(str(campaign_id))

        campaign.status = CampaignStatus.SENDING
        await self.repository.session.flush()
        result = await self.repository.get_with_relations(campaign_id)
        if not result:
            raise NotFoundError(str(campaign_id))
        return result

    async def estimate_recipients(
        self,
        criteria: CampaignCriteriaInput,
        sample_limit: int = 10,
    ) -> tuple[int, list[Contact]]:
        """Estimate recipients count for given criteria.

        Args:
            criteria: The criteria to evaluate
            sample_limit: Maximum number of sample contacts to return

        Returns:
            Tuple of (total count, list of sample Contact objects)
        """
        count = await self.criteria_evaluator.count_matching_contacts(criteria)
        sample_contacts = await self.criteria_evaluator.get_sample_contacts(
            criteria, limit=sample_limit
        )
        return count, sample_contacts

    async def get_campaign_recipients(
        self,
        campaign_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CampaignRecipient]:
        """Get recipients for a campaign with pagination."""
        if not await self.repository.exists(campaign_id):
            raise NotFoundError(str(campaign_id))
        return await self.recipients_repository.get_by_campaign_id(
            campaign_id, limit, offset
        )

    async def refresh_dynamic_recipients(self, campaign_id: UUID) -> Campaign:
        """Refresh recipients for a dynamic campaign based on criteria."""
        campaign = await self.repository.get_with_relations(campaign_id)
        if not campaign:
            raise NotFoundError(str(campaign_id))

        if campaign.recipient_list_type != RecipientListType.DYNAMIC:
            raise ValueError("Campaign is not a dynamic campaign")

        if not campaign.criteria:
            raise ValueError("Dynamic campaign has no criteria defined")

        criteria = self._dict_to_criteria(campaign.criteria.criteria_json)
        current_contacts = await self.criteria_evaluator.evaluate_criteria(criteria)
        current_contact_ids = {c.id for c in current_contacts}

        existing_contact_ids = (
            await self.recipients_repository.get_contact_ids_for_campaign(campaign_id)
        )

        new_contact_ids = current_contact_ids - existing_contact_ids
        if new_contact_ids:
            new_recipients = [
                CampaignRecipient(
                    campaign_id=campaign_id,
                    contact_id=contact_id,
                    email_status=EmailStatus.PENDING,
                )
                for contact_id in new_contact_ids
            ]
            _ = await self.recipients_repository.bulk_create(new_recipients)

        result = await self.repository.get_with_relations(campaign_id)
        if not result:
            raise NotFoundError(str(campaign_id))
        return result

    def _dict_to_criteria(
        self,
        criteria_dict: dict[str, Any],
    ) -> CampaignCriteriaInput:
        """Convert stored JSON back to CampaignCriteriaInput."""
        groups = []
        for group_dict in criteria_dict["groups"]:
            conditions = [
                CriteriaConditionInput(
                    entity_type=EntityType(cond["entity_type"]),
                    field=cond["field"],
                    operator=CriteriaOperator(cond["operator"]),
                    value=cond["value"],
                )
                for cond in group_dict["conditions"]
            ]
            groups.append(
                CriteriaGroupInput(
                    logical_operator=LogicalOperator(group_dict["logical_operator"]),
                    conditions=conditions,
                )
            )

        return CampaignCriteriaInput(
            groups=groups,
            group_operator=LogicalOperator(criteria_dict["group_operator"]),
        )
