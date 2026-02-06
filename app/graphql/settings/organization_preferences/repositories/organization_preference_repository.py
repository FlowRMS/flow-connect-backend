import uuid

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import func

from app.core.db.transient_session import TenantSession
from app.graphql.settings.organization_preferences.models.organization_preference import (
    OrganizationPreference,
)


class OrganizationPreferenceRepository:
    def __init__(self, session: TenantSession) -> None:
        self.session = session

    async def get_by_org_application_key(
        self,
        organization_id: uuid.UUID,
        application: str,
        key: str,
    ) -> OrganizationPreference | None:
        stmt = select(OrganizationPreference).where(
            OrganizationPreference.organization_id == organization_id,
            OrganizationPreference.application == application,
            OrganizationPreference.preference_key == key,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_org_and_application(
        self,
        organization_id: uuid.UUID,
        application: str,
    ) -> list[OrganizationPreference]:
        stmt = select(OrganizationPreference).where(
            OrganizationPreference.organization_id == organization_id,
            OrganizationPreference.application == application,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_by_org(
        self,
        organization_id: uuid.UUID,
    ) -> list[OrganizationPreference]:
        stmt = select(OrganizationPreference).where(
            OrganizationPreference.organization_id == organization_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert(
        self,
        organization_id: uuid.UUID,
        application: str,
        key: str,
        value: str | None,
    ) -> OrganizationPreference:
        stmt = (
            insert(OrganizationPreference)
            .values(
                id=uuid.uuid4(),
                organization_id=organization_id,
                application=application,
                preference_key=key,
                preference_value=value,
            )
            .on_conflict_do_update(
                constraint="uq_org_preferences_org_application_key",
                set_={
                    "preference_value": value,
                    "updated_at": func.now(),
                },
            )
            .returning(OrganizationPreference)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
