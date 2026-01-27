from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from commons.auth import AuthInfo, AuthService, ConnectionParams
from fastapi import Request, WebSocket
from graphql import GraphQLError
from pydantic import ValidationError
from starlette.datastructures import Headers
from strawberry.fastapi import BaseContext


class ContextModel:
    def __init__(self, auth_info: AuthInfo):
        super().__init__()
        self.auth_info = auth_info


class Context(BaseContext):
    def __init__(self) -> None:
        super().__init__()
        self.auth_info: AuthInfo = None  # type: ignore[assignment] # pyright: ignore[reportAttributeAccessIssue]
        self.aioinject_context: Any = None  # Added for aioinject extension
        self.commission_visible: bool = True

    def initialize(
        self, context: ContextModel, *, commission_visible: bool = True
    ) -> None:
        self.auth_info = context.auth_info
        self.commission_visible = commission_visible

    @classmethod
    @asynccontextmanager
    async def set_context(
        cls, request: Request | WebSocket, auth_service: AuthService
    ) -> AsyncGenerator[ContextModel, None]:
        auth_result = await auth_service.generate_auth_info_from_request(request)
        if auth_result.is_err():
            raise GraphQLError(
                message=f"Unauthorized. {auth_result.unwrap_err()}",
                extensions={"statusCode": 401, "type": "AuthenticationError"},
            )

        auth_info = auth_result.unwrap()
        yield ContextModel(auth_info=auth_info)

    @property
    def headers(self) -> Headers | None:
        return self.request.headers if self.request else None

    @property
    def connection_params_info(self) -> ConnectionParams:
        connection_params: dict[str, str] | None = self.connection_params

        if connection_params is None:
            raise ValidationError("Request not found")

        token: str | None = connection_params.get("Authorization", None)

        if token is None:
            raise ValidationError("Access token not found")

        return ConnectionParams(access_token=token)


async def get_context():
    return Context()
