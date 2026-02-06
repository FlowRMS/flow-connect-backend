import uuid
from typing import Any

from sqlalchemy import delete, exists, func, select
from sqlalchemy.orm import joinedload

from app.core.db.transient_session import TenantSession
from app.graphql.pos.data_exchange.models.enums import ExchangeFileStatus
from app.graphql.pos.data_exchange.models.exchange_file import ExchangeFile
from app.graphql.pos.validations.constants import BLOCKING_VALIDATION_KEYS
from app.graphql.pos.validations.models import FileValidationIssue


class FileValidationIssueRepository:
    def __init__(self, session: TenantSession) -> None:
        self.session = session

    async def create_bulk(self, issues: list[FileValidationIssue]) -> None:
        self.session.add_all(issues)
        await self.session.flush(issues)

    async def get_by_id(
        self, issue_id: uuid.UUID, *, load_file: bool = True
    ) -> FileValidationIssue | None:
        stmt = select(FileValidationIssue).where(FileValidationIssue.id == issue_id)
        if load_file:
            stmt = stmt.options(joinedload(FileValidationIssue.exchange_file))
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_by_pending_files(self) -> list[FileValidationIssue]:
        stmt = (
            select(FileValidationIssue)
            .join(FileValidationIssue.exchange_file)
            .where(ExchangeFile.status == ExchangeFileStatus.PENDING.value)
            .options(joinedload(FileValidationIssue.exchange_file))
            .order_by(FileValidationIssue.row_number)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def get_by_file_id(
        self, exchange_file_id: uuid.UUID
    ) -> list[FileValidationIssue]:
        stmt = (
            select(FileValidationIssue)
            .where(FileValidationIssue.exchange_file_id == exchange_file_id)
            .order_by(FileValidationIssue.row_number)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_file_and_key(
        self, exchange_file_id: uuid.UUID, validation_key: str
    ) -> list[FileValidationIssue]:
        stmt = (
            select(FileValidationIssue)
            .join(FileValidationIssue.exchange_file)
            .where(
                FileValidationIssue.exchange_file_id == exchange_file_id,
                FileValidationIssue.validation_key == validation_key,
                ExchangeFile.status == ExchangeFileStatus.PENDING.value,
            )
            .options(joinedload(FileValidationIssue.exchange_file))
            .order_by(FileValidationIssue.row_number)
        )
        result = await self.session.execute(stmt)
        return list(result.unique().scalars().all())

    async def delete_by_file_id(self, exchange_file_id: uuid.UUID) -> int:
        stmt = delete(FileValidationIssue).where(
            FileValidationIssue.exchange_file_id == exchange_file_id
        )
        result: Any = await self.session.execute(stmt)
        return result.rowcount

    async def count_blocking_issues(
        self,
        exchange_file_id: uuid.UUID,
        blocking_validation_keys: list[str],
    ) -> int:
        stmt = select(func.count()).where(
            FileValidationIssue.exchange_file_id == exchange_file_id,
            FileValidationIssue.validation_key.in_(blocking_validation_keys),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def has_blocking_issues_for_pending_files(self, org_id: uuid.UUID) -> bool:
        stmt = select(
            exists().where(
                FileValidationIssue.exchange_file_id == ExchangeFile.id,
                ExchangeFile.org_id == org_id,
                ExchangeFile.status == ExchangeFileStatus.PENDING.value,
                FileValidationIssue.validation_key.in_(BLOCKING_VALIDATION_KEYS),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def count_blocking_issues_for_all_pending_files(
        self, org_id: uuid.UUID
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(FileValidationIssue)
            .join(ExchangeFile, FileValidationIssue.exchange_file_id == ExchangeFile.id)
            .where(
                ExchangeFile.org_id == org_id,
                ExchangeFile.status == ExchangeFileStatus.PENDING.value,
                FileValidationIssue.validation_key.in_(BLOCKING_VALIDATION_KEYS),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
