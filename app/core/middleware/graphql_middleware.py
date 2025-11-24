from collections.abc import AsyncGenerator
from typing import override

from commons.auth import AuthService
from loguru import logger
from starlette.websockets import WebSocket
from strawberry.extensions import SchemaExtension

from app.core.container import create_container
from app.core.context import Context
from app.core.context_wrapper import ContextWrapper


class GraphQLMiddleware(SchemaExtension):
    @override
    async def on_execute(self) -> AsyncGenerator[None, None]:
        ctx = self.execution_context
        logger.info(f"[{ctx.query}] vars='{ctx.variables}'")
        yield

    @override
    async def on_operation(self) -> AsyncGenerator[None, None]:
        """Handle operation lifecycle including authentication and session management."""
        context: Context = self.execution_context.context

        temp_request = context.request

        if isinstance(temp_request, WebSocket):
            temp_request = self.execution_context.context.connection_params_info

        if context.request is None:
            logger.error("Request is None")
            yield
            return

        async with create_container().context() as conn_ctx:
            async with Context.set_context(
                request=temp_request,  # pyright: ignore[reportArgumentType]
                auth_service=await conn_ctx.resolve(AuthService),
            ) as context_model:
                context.initialize(context_model)
                context_wrapper = await conn_ctx.resolve(ContextWrapper)
                wrapper_token = context_wrapper.set(context)
                yield
                context_wrapper.reset(wrapper_token)
