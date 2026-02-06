import uuid

from app.core.flow_connect_api import FlowConnectApiClient, raise_for_api_status


class ConnectionRequestService:
    def __init__(self, api_client: FlowConnectApiClient) -> None:
        self.api_client = api_client

    async def create_connection_request(
        self,
        target_org_id: uuid.UUID,
        *,
        draft: bool = False,
    ) -> bool:
        response = await self.api_client.post(
            "/connections/requests",
            {"target_org_id": str(target_org_id), "draft": draft},
        )
        raise_for_api_status(
            response,
            entity_id=str(target_org_id),
            context="Creating connection request",
        )
        return True

    async def invite_connection(self, target_org_id: uuid.UUID) -> bool:
        response = await self.api_client.post(
            f"/connections/org/{target_org_id}/invite",
            {},
        )
        raise_for_api_status(
            response,
            entity_id=str(target_org_id),
            context="Inviting connection",
        )
        return True
