import asyncio
import contextlib
import logging
import time
from typing import Any

from aioinject.ext.fastapi import AioInjectMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import configure_mappers

# from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api.auth_router import router as auth_router
from app.api.o365_router import router as o365_router
from app.core.container import create_container
from app.graphql.app import create_graphql_app

logger = logging.getLogger(__name__)


async def _run_campaign_worker() -> None:
    """Background task that runs the campaign email worker."""
    from app.workers.campaign_worker import check_and_process_campaigns

    logger.info("Campaign worker starting...")
    while True:
        try:
            logger.info("Checking for campaigns to process...")
            result = await check_and_process_campaigns()
            logger.info(f"Campaign check result: {result}")
        except Exception as e:
            logger.exception(f"Error in campaign worker: {e}")
        await asyncio.sleep(60)  # Run every 60 seconds


def create_app() -> FastAPI:
    container = create_container()

    @contextlib.asynccontextmanager
    async def lifespan(_app: FastAPI):
        configure_mappers()
        async with container:
            # Start the campaign worker as a background task
            worker_task = asyncio.create_task(_run_campaign_worker())
            logger.info("Campaign email worker started as background task")
            try:
                yield
            finally:
                # Cancel the worker task when the app shuts down
                worker_task.cancel()
                try:
                    await worker_task
                except asyncio.CancelledError:
                    logger.info("Campaign worker stopped")

    app = FastAPI(
        title="Flow Py Report Backend API",
        description="Backend API for Flow Py Report built with FastAPI and Strawberry GraphQL",
        version="0.0.1",
        lifespan=lifespan,
        openapi_url=None,
    )
    app.add_middleware(AioInjectMiddleware, container=container)
    app.include_router(create_graphql_app(), prefix="/graphql")
    app.include_router(auth_router, prefix="/api")
    app.include_router(o365_router, prefix="/api")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        # allow_origin_regex=r"https?://.*\.?flowrms\.com",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # app.add_middleware(
    #     TrustedHostMiddleware,
    #     allowed_hosts=["*.flowrms.com", "flowrms.com", "localhost", "127.0.0.1"],
    # )

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: Any) -> JSONResponse:  # pyright: ignore[reportUnusedFunction]
        try:
            start_time = time.perf_counter()
            response = await call_next(request)
            process_time = time.perf_counter() - start_time
            process_time = round(process_time * 1000, 2)
            response.headers["X-Process-Time-Ms"] = f"{process_time}ms"
        except Exception:
            import traceback

            return JSONResponse(
                status_code=500, content={"detail": traceback.format_exc()}
            )

        return response

    @app.get("/api/health", include_in_schema=True)
    def health_check():  # pyright: ignore[reportUnusedFunction]
        return {"status": "ok"}

    return app
