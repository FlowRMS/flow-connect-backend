import os

import strawberry
from aioinject import Injected

from app.graphql.di import inject
from app.graphql.geography.strawberry.geography_types import SubdivisionResponse
from app.graphql.organizations.services import OrganizationSearchService
from app.graphql.organizations.strawberry import OrganizationLiteResponse


@strawberry.type
class ConnectionQueries:
    @strawberry.field()
    @inject
    async def connection_search(
        self,
        search_term: str,
        service: Injected[OrganizationSearchService],
        active: bool | None = True,
        flow_connect_member: bool | None = None,
        connected: bool | None = None,
        limit: int = 20,
        rep_firms: bool = False,
    ) -> list[OrganizationLiteResponse]:
        if not os.environ.get("ORGS_DB_URL"):
            return []
        results = await service.search_for_connections(
            search_term,
            active=active,
            flow_connect_member=flow_connect_member,
            connected=connected,
            limit=limit,
            rep_firms=rep_firms,
        )
        return [
            OrganizationLiteResponse.from_orm_model(
                result.org,
                flow_connect_member=result.flow_connect_member,
                pos_contacts=result.pos_contacts,
                connection_status=result.connection_status,
                agreement_data=result.agreement_data,
                subdivisions=[
                    SubdivisionResponse.from_model(s) for s in result.subdivisions
                ]
                if result.subdivisions
                else None,
            )
            for result in results
        ]
