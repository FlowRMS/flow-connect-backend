from typing import Any

from strawberry.fastapi import GraphQLRouter

from app.core.context import get_context
from app.graphql.schemas.schema import schema


def create_graphql_app():
    router: Any = GraphQLRouter(
        schema,
        context_getter=get_context,
        multipart_uploads_enabled=True,
    )
    return router
