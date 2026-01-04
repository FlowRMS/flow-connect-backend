import contextlib
from collections.abc import AsyncIterator

import aiohttp
import aioinject
from commons.dtos.common.dto_loader_service import DTOLoaderService
from commons.s3.service import S3Service


@contextlib.asynccontextmanager
async def create_aiohttp_session() -> AsyncIterator[aiohttp.ClientSession]:
    async with aiohttp.ClientSession() as session:
        yield session


async def create_dto_loader_service(
    s3_service: S3Service, aiohttp_session: aiohttp.ClientSession
) -> DTOLoaderService:
    return DTOLoaderService(s3_service, aiohttp_session)


providers = [
    aioinject.Scoped(create_aiohttp_session),
    aioinject.Scoped(create_dto_loader_service),
]
