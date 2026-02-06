import uuid

from commons.db.controller import MultiTenantController
from commons.db.models.tenant import Tenant
from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.graphql.pos.data_exchange.models import (
    ExchangeFile,
    ReceivedExchangeFile,
    ReceivedExchangeFileStatus,
)


class CrossTenantDeliveryService:
    def __init__(self, controller: MultiTenantController) -> None:
        self.controller = controller

    async def resolve_tenant_url(self, org_id: uuid.UUID) -> str | None:
        async with self.controller.base_scoped_session() as session:
            stmt = select(Tenant.url).where(Tenant.org_id == org_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def deliver_files(self, files: list[ExchangeFile]) -> None:
        for file in files:
            for target in file.target_organizations:
                await self._deliver_to_target(file, target.connected_org_id)

    async def _deliver_to_target(
        self, file: ExchangeFile, target_org_id: uuid.UUID
    ) -> None:
        try:
            tenant_url = await self.resolve_tenant_url(target_org_id)
            if tenant_url is None:
                logger.warning(
                    f"Tenant not found for org_id={target_org_id}, skipping delivery"
                )
                return

            await self._insert_received_file(file, target_org_id, tenant_url)
        except IntegrityError:
            # Duplicate key - file already delivered, idempotent behavior
            logger.info(
                f"File {file.id} already delivered to org {target_org_id} (duplicate)"
            )
        except Exception as e:
            # Log and continue - error isolation per target
            logger.error(
                f"Failed to deliver file {file.id} to org {target_org_id}: {e}"
            )

    async def _insert_received_file(
        self, file: ExchangeFile, target_org_id: uuid.UUID, tenant_url: str
    ) -> None:
        async with self.controller.scoped_session(tenant_url) as session:
            async with session.begin():
                received_file = ReceivedExchangeFile(
                    org_id=target_org_id,
                    sender_org_id=file.org_id,
                    s3_key=file.s3_key,
                    file_name=file.file_name,
                    file_size=file.file_size,
                    file_sha=file.file_sha,
                    file_type=file.file_type,
                    row_count=file.row_count,
                    reporting_period=file.reporting_period,
                    is_pos=file.is_pos,
                    is_pot=file.is_pot,
                    status=ReceivedExchangeFileStatus.NEW.value,
                )
                session.add(received_file)
                await session.flush([received_file])
                logger.info(
                    f"Delivered file {file.id} to org {target_org_id} "
                    f"(received_file_id={received_file.id})"
                )
