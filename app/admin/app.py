from typing import Any

from strawberry.fastapi import GraphQLRouter

from app.admin.context import get_admin_context
from app.admin.schemas.schema import admin_schema


def create_admin_graphql_app() -> GraphQLRouter[Any, Any]:
    router: Any = GraphQLRouter(
        admin_schema,
        context_getter=get_admin_context,
    )
    return router
