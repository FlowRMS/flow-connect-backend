"""Central module to import all ORM models and configure mappers.

Importing this module ensures all SQLAlchemy models are registered
with the mapper before relationships are resolved. This is necessary
for workers and other standalone processes that don't go through
the FastAPI lifespan.
"""

# Import all models to register them with SQLAlchemy's mapper
# Campaign models
from commons.db.v6.crm.campaigns.campaign_criteria_model import CampaignCriteria
from commons.db.v6.crm.campaigns.campaign_model import Campaign
from commons.db.v6.crm.campaigns.campaign_recipient_model import CampaignRecipient
from commons.db.v6.crm.campaigns.campaign_send_log_model import CampaignSendLog

# Company model
from commons.db.v6.crm.companies.company_model import Company

# Contact model (required for CampaignRecipient.contact relationship)
from commons.db.v6.crm.contact_model import Contact
from commons.db.v6.crm.jobs.jobs_model import Job
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from commons.db.v6.crm.notes.note_conversation_model import NoteConversation
from commons.db.v6.crm.notes.note_model import Note
from commons.db.v6.crm.pre_opportunities.pre_opportunity_balance_model import (
    PreOpportunityBalance,
)
from commons.db.v6.crm.pre_opportunities.pre_opportunity_detail_model import (
    PreOpportunityDetail,
)
from commons.db.v6.crm.pre_opportunities.pre_opportunity_model import PreOpportunity
from commons.db.v6.crm.tasks.task_conversation_model import TaskConversation
from commons.db.v6.crm.tasks.task_model import Task
from sqlalchemy.orm import configure_mappers

__all__ = [
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
