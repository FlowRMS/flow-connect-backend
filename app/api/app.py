import contextlib
import time
from pathlib import Path
from typing import Any

from aioinject.ext.fastapi import AioInjectMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import configure_mappers

# from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.api.auth_router import router as auth_router
from app.api.o365_router import router as o365_router
from app.api.pdf_proxy_router import router as pdf_proxy_router
from app.core.container import create_container
from app.graphql.app import create_graphql_app

# Define uploads directory
UPLOADS_DIR = Path(__file__).parent.parent.parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)


def create_app() -> FastAPI:
    container = create_container()

    @contextlib.asynccontextmanager
    async def lifespan(_app: FastAPI):
        configure_mappers()
        async with container:
            yield

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
    app.include_router(pdf_proxy_router, prefix="/api")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001", "https://flowrms.com", "https://www.flowrms.com"],
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

    # Mount static files for uploads
    app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

    return app
