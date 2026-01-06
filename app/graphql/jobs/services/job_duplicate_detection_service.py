import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from commons.auth import AuthInfo
from commons.db.v6.crm.jobs import Job
from commons.db.v6.crm.links.entity_type import EntityType
from loguru import logger

from app.core.config.vector_settings import VectorSettings
from app.graphql.jobs.repositories.confirmed_different_repository import (
    ConfirmedDifferentJobRepository,
)
from app.graphql.jobs.repositories.jobs_repository import JobsRepository
from app.graphql.jobs.services.job_embedding_service import JobEmbeddingService
from app.graphql.links.services.links_service import LinksService


@dataclass
class SimilarJobResult:
    job: Job
    confidence: Decimal
    match_reasons: list[str] = field(default_factory=list)


@dataclass
class DuplicateJobGroup:
    id: uuid.UUID
    jobs: list[Job]
    confidence: Decimal
    match_reasons: list[str] = field(default_factory=list)


@dataclass
class DuplicateScanResult:
    groups: list[DuplicateJobGroup]
    total_jobs_scanned: int


class JobDuplicateDetectionService:
    def __init__(
        self,
        embedding_service: JobEmbeddingService,
        jobs_repository: JobsRepository,
        confirmed_different_repository: ConfirmedDifferentJobRepository,
        links_service: LinksService,
        settings: VectorSettings,
        auth_info: AuthInfo,
    ) -> None:
        super().__init__()
        self.embedding_service = embedding_service
        self.jobs_repository = jobs_repository
        self.confirmed_different_repository = confirmed_different_repository
        self.links_service = links_service
        self.settings = settings
        self.auth_info = auth_info
        self._links_cache: dict[uuid.UUID, dict[EntityType, set[uuid.UUID]]] = {}

    def _clear_cache(self) -> None:
        self._links_cache.clear()

    async def _get_job_linked_entities(
        self,
        job_id: uuid.UUID,
    ) -> dict[EntityType, set[uuid.UUID]]:
        if job_id in self._links_cache:
            return self._links_cache[job_id]

        links = await self.links_service.get_links_for_entity(EntityType.JOB, job_id)
        entities: dict[EntityType, set[uuid.UUID]] = {}
        for link in links:
            if link.source_entity_id == job_id:
                entity_type = link.target_entity_type
                entity_id = link.target_entity_id
            else:
                entity_type = link.source_entity_type
                entity_id = link.source_entity_id
            if entity_type not in entities:
                entities[entity_type] = set()
            entities[entity_type].add(entity_id)

        self._links_cache[job_id] = entities
        return entities

    async def _generate_match_reasons(
        self,
        job1: Job,
        job2: Job,
        score: float,
    ) -> list[str]:
        reasons: list[str] = []

        confidence_pct = int(score * 100)
        reasons.append(f"{confidence_pct}% semantic similarity")

        if job1.job_name and job2.job_name:
            name1_lower = job1.job_name.lower()
            name2_lower = job2.job_name.lower()
            if name1_lower == name2_lower:
                reasons.append("Identical job names")
            elif name1_lower in name2_lower or name2_lower in name1_lower:
                reasons.append("Similar job names")

        if job1.job_type and job2.job_type and job1.job_type == job2.job_type:
            reasons.append(f"Same job type: {job1.job_type}")

        job1_entities = await self._get_job_linked_entities(job1.id)
        job2_entities = await self._get_job_linked_entities(job2.id)

        for entity_type in [
            EntityType.CUSTOMER,
            EntityType.CONTACT,
            EntityType.COMPANY,
        ]:
            if entity_type in job1_entities and entity_type in job2_entities:
                shared = job1_entities[entity_type] & job2_entities[entity_type]
                if shared:
                    type_name = entity_type.name.lower()
                    reasons.append(f"Shared {type_name}(s)")

        if job1.tags and job2.tags:
            shared_tags = set(job1.tags) & set(job2.tags)
            if shared_tags:
                reasons.append(f"Shared tags: {', '.join(list(shared_tags)[:3])}")

        return reasons

    async def find_similar_jobs(
        self,
        job: Job,
        threshold: float | None = None,
        limit: int = 10,
    ) -> list[SimilarJobResult]:
        if threshold is None:
            threshold = self.settings.duplicate_threshold

        similar_ids = await self.embedding_service.search_similar(
            job=job,
            limit=limit,
            threshold=threshold,
        )

        filtered_ids = (
            await self.confirmed_different_repository.filter_confirmed_different_pairs(
                job_id=job.id,
                candidate_ids=[sid for sid, _ in similar_ids],
            )
        )
        filtered_set = set(filtered_ids)
        similar_ids = [
            (sid, score) for sid, score in similar_ids if sid in filtered_set
        ]

        results: list[SimilarJobResult] = []
        for similar_id, score in similar_ids:
            similar_job = await self.jobs_repository.get_by_id(similar_id)
            if similar_job:
                reasons = await self._generate_match_reasons(job, similar_job, score)
                results.append(
                    SimilarJobResult(
                        job=similar_job,
                        confidence=Decimal(str(round(score, 4))),
                        match_reasons=reasons,
                    )
                )
        return results

    async def scan_for_duplicates(
        self,
        job_id: uuid.UUID | None = None,
        status_filter: list[str] | None = None,
        days_back: int | None = None,
    ) -> DuplicateScanResult:
        self._clear_cache()

        if job_id:
            job = await self.jobs_repository.get_by_id(job_id)
            if not job:
                return DuplicateScanResult(groups=[], total_jobs_scanned=0)
            jobs_to_scan = [job]
        else:
            all_jobs = await self.jobs_repository.list_all()
            jobs_to_scan = all_jobs

            if status_filter:
                status_set = set(status_filter)
                jobs_to_scan = [
                    j for j in jobs_to_scan if j.status and j.status.name in status_set
                ]

            if days_back is not None:
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
                jobs_to_scan = [
                    j for j in jobs_to_scan if j.created_at and j.created_at >= cutoff_date
                ]

        total_jobs = len(jobs_to_scan)
        logger.info(f"[1/4] Scan initialized | {total_jobs} jobs to process")

        logger.info(f"[2/4] Checking embeddings for {total_jobs} jobs...")
        jobs_needing_embeddings: list[Job] = []
        for i, job in enumerate(jobs_to_scan):
            if await self.embedding_service.needs_update(job):
                jobs_needing_embeddings.append(job)
            if (i + 1) % 500 == 0:
                logger.info(f"[2/4] Progress: {i + 1}/{total_jobs}")

        cached = total_jobs - len(jobs_needing_embeddings)
        logger.info(f"[2/4] Done | Cached: {cached}, New: {len(jobs_needing_embeddings)}")

        if jobs_needing_embeddings:
            logger.info(f"[3/4] Generating {len(jobs_needing_embeddings)} embeddings...")
            _ = await self.embedding_service.upsert_job_embeddings_batch(jobs_needing_embeddings)
            logger.info("[3/4] Embedding generation complete")
        else:
            logger.info("[3/4] Skipped (all cached)")

        logger.info(f"[4/4] Similarity search | {total_jobs} jobs...")
        pairs: list[tuple[uuid.UUID, uuid.UUID, float, list[str]]] = []
        for i, job in enumerate(jobs_to_scan):
            for result in await self.find_similar_jobs(job):
                id1, id2 = (job.id, result.job.id) if job.id < result.job.id else (result.job.id, job.id)
                pairs.append((id1, id2, float(result.confidence), result.match_reasons))
            if (i + 1) % 100 == 0 or i == total_jobs - 1:
                logger.info(f"[4/4] {i + 1}/{total_jobs} ({(i + 1) * 100 // total_jobs}%) | {len(pairs)} pairs")

        logger.info(f"[Clustering] {len(pairs)} pairs...")
        groups = self._cluster_duplicates(pairs, jobs_to_scan)
        logger.info(f"[Done] {total_jobs} scanned, {len(groups)} groups found")

        self._clear_cache()
        return DuplicateScanResult(groups=groups, total_jobs_scanned=len(jobs_to_scan))

    def _cluster_duplicates(
        self,
        pairs: list[tuple[uuid.UUID, uuid.UUID, float, list[str]]],
        all_jobs: list[Job],
    ) -> list[DuplicateJobGroup]:
        parent: dict[uuid.UUID, uuid.UUID] = {}

        def find(x: uuid.UUID) -> uuid.UUID:
            if x not in parent:
                parent[x] = x
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x: uuid.UUID, y: uuid.UUID) -> None:
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        pair_data: dict[tuple[uuid.UUID, uuid.UUID], tuple[float, list[str]]] = {}
        for id1, id2, score, reasons in pairs:
            key = (id1, id2) if id1 < id2 else (id2, id1)
            if key not in pair_data or score > pair_data[key][0]:
                pair_data[key] = (score, reasons)
            union(id1, id2)

        clusters: dict[uuid.UUID, list[uuid.UUID]] = {}
        for job_id in parent:
            root = find(job_id)
            if root not in clusters:
                clusters[root] = []
            clusters[root].append(job_id)

        job_map = {j.id: j for j in all_jobs}
        groups: list[DuplicateJobGroup] = []

        for cluster_ids in clusters.values():
            if len(cluster_ids) < 2:
                continue

            cluster_jobs = [job_map[jid] for jid in cluster_ids if jid in job_map]
            if len(cluster_jobs) < 2:
                continue

            max_score = 0.0
            all_reasons: list[str] = []
            for i, id1 in enumerate(cluster_ids):
                for id2 in cluster_ids[i + 1 :]:
                    key = (id1, id2) if id1 < id2 else (id2, id1)
                    if key in pair_data:
                        score, reasons = pair_data[key]
                        max_score = max(max_score, score)
                        all_reasons.extend(reasons)

            unique_reasons = list(dict.fromkeys(all_reasons))
            groups.append(
                DuplicateJobGroup(
                    id=uuid.uuid4(),
                    jobs=cluster_jobs,
                    confidence=Decimal(str(round(max_score, 4))),
                    match_reasons=unique_reasons[:5],
                )
            )

        return sorted(groups, key=lambda g: g.confidence, reverse=True)
