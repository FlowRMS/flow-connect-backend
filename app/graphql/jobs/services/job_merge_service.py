import uuid
from dataclasses import dataclass
from typing import Any, cast

from commons.auth import AuthInfo
from commons.db.v6.crm.jobs import Job
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from sqlalchemy import CursorResult, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapper

from app.errors.common_errors import NotFoundError
from app.graphql.jobs.repositories.jobs_repository import JobsRepository
from app.graphql.jobs.services.job_embedding_service import JobEmbeddingService
from app.graphql.links.services.links_service import LinksService


@dataclass
class FieldSelection:
    field_name: str
    source_job_id: uuid.UUID


@dataclass
class MergeResult:
    merged_job: Job
    jobs_deleted_count: int
    entities_transferred_count: int


def _get_mergeable_fields() -> list[str]:
    mapper: Mapper[Job] = Job.__mapper__
    return [
        col.key
        for col in mapper.columns
        if col.info.get("mergeable", False)
    ]


class JobMergeService:
    def __init__(
        self,
        jobs_repository: JobsRepository,
        links_service: LinksService,
        embedding_service: JobEmbeddingService,
        session: AsyncSession,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.jobs_repository = jobs_repository
        self.links_service = links_service
        self.embedding_service = embedding_service
        self.session = session
        self.auth_info = auth_info

    async def merge_jobs(
        self,
        primary_job_id: uuid.UUID,
        duplicate_job_ids: list[uuid.UUID],
        field_selections: list[FieldSelection] | None = None,
    ) -> MergeResult:
        primary_job = await self.jobs_repository.get_by_id(primary_job_id)
        if not primary_job:
            raise NotFoundError(f"Primary job {primary_job_id} not found")

        duplicate_jobs: list[Job] = []
        for dup_id in duplicate_job_ids:
            dup_job = await self.jobs_repository.get_by_id(dup_id)
            if not dup_job:
                raise NotFoundError(f"Duplicate job {dup_id} not found")
            duplicate_jobs.append(dup_job)

        all_jobs = {primary_job.id: primary_job}
        for dup in duplicate_jobs:
            all_jobs[dup.id] = dup

        if field_selections:
            primary_job = self._apply_field_selections(
                primary_job,
                all_jobs,
                field_selections,
            )
            _ = await self.jobs_repository.update(primary_job)

        total_transferred = 0
        for dup_job in duplicate_jobs:
            transferred = await self._transfer_linked_entities(
                from_job_id=dup_job.id,
                to_job_id=primary_job.id,
            )
            total_transferred += transferred

            fk_transferred = await self._transfer_direct_foreign_keys(
                from_job_id=dup_job.id,
                to_job_id=primary_job.id,
            )
            total_transferred += fk_transferred

        for dup_job in duplicate_jobs:
            _ = await self.embedding_service.delete_job_embedding(dup_job.id)
            _ = await self.jobs_repository.delete(dup_job.id)

        _ = await self.embedding_service.upsert_job_embedding(primary_job)

        updated_job = await self.jobs_repository.get_by_id(primary_job_id)
        if not updated_job:
            raise NotFoundError(f"Primary job {primary_job_id} not found after merge")

        return MergeResult(
            merged_job=updated_job,
            jobs_deleted_count=len(duplicate_jobs),
            entities_transferred_count=total_transferred,
        )

    def _apply_field_selections(
        self,
        primary_job: Job,
        all_jobs: dict[uuid.UUID, Job],
        selections: list[FieldSelection],
    ) -> Job:
        mergeable_fields = _get_mergeable_fields()
        for selection in selections:
            if selection.field_name not in mergeable_fields:
                continue
            if selection.source_job_id not in all_jobs:
                continue

            source_job = all_jobs[selection.source_job_id]
            value = getattr(source_job, selection.field_name, None)
            setattr(primary_job, selection.field_name, value)

        return primary_job

    async def _transfer_linked_entities(
        self,
        from_job_id: uuid.UUID,
        to_job_id: uuid.UUID,
    ) -> int:
        links = await self.links_service.get_links_for_entity(
            EntityType.JOB,
            from_job_id,
        )

        transferred_count = 0
        for link in links:
            if (
                link.source_entity_type == EntityType.JOB
                and link.source_entity_id == from_job_id
            ):
                new_link = await self._create_link_if_not_exists(
                    source_type=EntityType.JOB,
                    source_id=to_job_id,
                    target_type=link.target_entity_type,
                    target_id=link.target_entity_id,
                )
            else:
                new_link = await self._create_link_if_not_exists(
                    source_type=link.source_entity_type,
                    source_id=link.source_entity_id,
                    target_type=EntityType.JOB,
                    target_id=to_job_id,
                )

            if new_link:
                transferred_count += 1

        return transferred_count

    async def _create_link_if_not_exists(
        self,
        source_type: EntityType,
        source_id: uuid.UUID,
        target_type: EntityType,
        target_id: uuid.UUID,
    ) -> LinkRelation | None:
        try:
            return await self.links_service.create_link(
                source_type=source_type,
                source_id=source_id,
                target_type=target_type,
                target_id=target_id,
            )
        except Exception:
            return None

    async def _transfer_direct_foreign_keys(
        self,
        from_job_id: uuid.UUID,
        to_job_id: uuid.UUID,
    ) -> int:
        tables_with_job_fk = [
            "pycrm.quotes",
            "pycrm.pre_opportunities",
            "pycommission.orders",
        ]

        total_updated = 0
        for table in tables_with_job_fk:
            result = await self.session.execute(
                text(f"UPDATE {table} SET job_id = :to_id WHERE job_id = :from_id"),
                {"to_id": to_job_id, "from_id": from_job_id},
            )
            cursor_result = cast(CursorResult[Any], result)
            total_updated += cursor_result.rowcount or 0

        await self.session.flush()
        return total_updated
