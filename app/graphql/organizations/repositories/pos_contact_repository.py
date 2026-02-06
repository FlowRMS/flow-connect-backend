import uuid
from dataclasses import dataclass

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graphql.organizations.models import (
    RemoteAppRole,
    RemoteOrgMembership,
    RemoteUser,
    RemoteUserAppRole,
)


@dataclass
class PosContactData:
    id: uuid.UUID
    name: str | None
    email: str | None


@dataclass
class OrgPosContacts:
    contacts: list[PosContactData]
    total_count: int


class PosContactRepository:
    FLOW_POS_ROLE_KEY = "flow-pos"
    MAX_CONTACTS_PER_ORG = 5

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    @staticmethod
    def _build_full_name(first_name: str | None, last_name: str | None) -> str | None:
        parts = [p for p in (first_name, last_name) if p]
        return " ".join(parts) if parts else None

    async def get_pos_contacts_for_orgs(
        self,
        org_ids: list[uuid.UUID],
    ) -> dict[uuid.UUID, OrgPosContacts]:
        if not org_ids:
            return {}

        # Subquery: users with flow-pos role
        flow_pos_users = (
            select(RemoteUserAppRole.user_id)
            .join(
                RemoteAppRole,
                RemoteUserAppRole.app_role_id == RemoteAppRole.id,
            )
            .where(RemoteAppRole.role_key == self.FLOW_POS_ROLE_KEY)
            .subquery()
        )

        # Main query: get contacts with org membership and flow-pos role
        stmt = (
            select(
                RemoteOrgMembership.org_id,
                RemoteUser.id,
                RemoteUser.first_name,
                RemoteUser.last_name,
                RemoteUser.email,
            )
            .join(RemoteUser, RemoteOrgMembership.user_id == RemoteUser.id)
            .where(
                and_(
                    RemoteOrgMembership.org_id.in_(org_ids),
                    RemoteOrgMembership.deleted_at.is_(None),
                    RemoteOrgMembership.user_id.in_(select(flow_pos_users)),
                )
            )
            .distinct()
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        # Group by org_id
        org_contacts: dict[uuid.UUID, list[PosContactData]] = {}
        for row in rows:
            org_id = row.org_id
            name = self._build_full_name(row.first_name, row.last_name)
            contact = PosContactData(id=row.id, name=name, email=row.email)
            if org_id not in org_contacts:
                org_contacts[org_id] = []
            org_contacts[org_id].append(contact)

        # Build result with limited contacts and total count
        result_dict: dict[uuid.UUID, OrgPosContacts] = {}
        for org_id in org_ids:
            contacts = org_contacts.get(org_id, [])
            result_dict[org_id] = OrgPosContacts(
                contacts=contacts[: self.MAX_CONTACTS_PER_ORG],
                total_count=len(contacts),
            )

        return result_dict
