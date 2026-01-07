from collections.abc import AsyncGenerator
from typing import override

from commons.auth import AuthInfo, AuthService
from commons.db.controller import MultiTenantController
from commons.db.v6 import RbacRoleSetting
from loguru import logger
from sqlalchemy import select
from starlette.websockets import WebSocket
from strawberry.extensions import SchemaExtension

from app.core.container import create_container
from app.core.context import Context
from app.core.context_wrapper import ContextWrapper
from app.core.db.db_provider import create_session


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
                controller = await conn_ctx.resolve(MultiTenantController)
                commission_visible = await self._get_commission_visibility(
                    controller,
                    context_model.auth_info,
                )
                context.initialize(context_model, commission_visible=commission_visible)
                context_wrapper = await conn_ctx.resolve(ContextWrapper)
                wrapper_token = context_wrapper.set(context)
                yield
                context_wrapper.reset(wrapper_token)

    async def _get_commission_visibility(
        self,
        multi_tenant_controller: MultiTenantController,
        auth_info: AuthInfo,
    ) -> bool:
        roles = auth_info.roles or []
        if not roles:
            return True

        try:
            async with create_session(
                multi_tenant_controller,
                auth_info,
            ) as session:
                primary_role = roles[0]
                stmt = select(RbacRoleSetting.commission).where(
                    RbacRoleSetting.role == primary_role
                )
                result = await session.execute(stmt)
                commission = result.scalar_one_or_none()

                return commission if commission is not None else True
        except Exception as e:
            logger.exception(f"Error fetching commission visibility: {e}")
            return True
