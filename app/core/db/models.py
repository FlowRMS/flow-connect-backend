"""Central module to import all ORM models and configure mappers.

Importing this module ensures all SQLAlchemy models are registered
with the mapper before relationships are resolved. This is necessary
for workers and other standalone processes that don't go through
the FastAPI lifespan.
"""

from sqlalchemy.orm import configure_mappers

# Other models that may have relationships
from app.graphql.addresses.models.address_model import CompanyAddress

# Import all models to register them with SQLAlchemy's mapper
# Campaign models
from app.graphql.campaigns.models.campaign_criteria_model import CampaignCriteria
from app.graphql.campaigns.models.campaign_model import Campaign
from app.graphql.campaigns.models.campaign_recipient_model import CampaignRecipient
from app.graphql.campaigns.models.campaign_send_log_model import CampaignSendLog

# Company model
from app.graphql.companies.models.company_model import Company

# Contact model (required for CampaignRecipient.contact relationship)
from app.graphql.contacts.models.contact_model import Contact
from app.graphql.jobs.models.jobs_model import Job
from app.graphql.links.models.link_relation_model import LinkRelation
from app.graphql.notes.models.note_conversation_model import NoteConversation
from app.graphql.notes.models.note_model import Note
from app.graphql.pre_opportunities.models.pre_opportunity_balance_model import (
    PreOpportunityBalance,
)
from app.graphql.pre_opportunities.models.pre_opportunity_detail_model import (
    PreOpportunityDetail,
)
from app.graphql.pre_opportunities.models.pre_opportunity_model import PreOpportunity
from app.graphql.tasks.models.task_conversation_model import TaskConversation
from app.graphql.tasks.models.task_model import Task

__all__ = [
    "CompanyAddress",
    "Campaign",
    "CampaignCriteria",
    "CampaignRecipient",
    "CampaignSendLog",
    "Company",
    "Contact",
    "Job",
    "LinkRelation",
    "Note",
    "NoteConversation",
    "PreOpportunity",
    "PreOpportunityBalance",
    "PreOpportunityDetail",
    "Task",
    "TaskConversation",
    "configure_mappers",
]
