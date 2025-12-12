"""SQLAlchemy ORM model for CampaignCriteria entity."""

from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.base import CrmBaseModel

if TYPE_CHECKING:
    from app.graphql.campaigns.models.campaign_model import Campaign


class CampaignCriteria(CrmBaseModel, kw_only=True):
    """Campaign criteria entity storing filter rules for recipient lists."""

    __tablename__ = "campaign_criteria"

    campaign_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("pycrm.campaigns.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    criteria_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_dynamic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    campaign: Mapped["Campaign"] = relationship(init=False, back_populates="criteria")
