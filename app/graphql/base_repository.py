import uuid
from typing import ClassVar, Generic, TypeVar
from uuid import UUID

from loguru import logger
import pendulum
from commons.db.v6 import BaseModel, RbacPrivilegeTypeEnum, RbacResourceEnum
from commons.db.v6.crm.links.entity_type import EntityType
from commons.db.v6.crm.links.link_relation_model import LinkRelation
from sqlalchemy import Result, Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from app.core.context_wrapper import ContextWrapper
from app.core.processors.base import BaseProcessor
from app.core.processors.context import EntityContext
from app.core.processors.events import RepositoryEvent
from app.core.processors.executor import ProcessorExecutor
from app.errors.common_errors import DeletionError, UnauthorizedError
from app.graphql.v2.rbac.services.rbac_filter_service import RbacFilterService
from app.graphql.v2.rbac.strategies.base import RbacFilterStrategy

T = TypeVar("T", bound=BaseModel)
GenQuery = TypeVar("GenQuery")


class BaseRepository(Generic[T]):
    """
    Base repository providing common CRUD operations.

    Type parameter T should be the SQLAlchemy model class.
    Subclasses can enable RBAC filtering by:
    1. Setting rbac_resource class attribute
    2. Overriding get_rbac_filter_strategy() to return a filter strategy
    3. Passing rbac_filter_service in __init__
    """

    entity_type: ClassVar[EntityType | None] = None
    rbac_resource: ClassVar[RbacResourceEnum | None] = None

    def __init__(
        self,
        session: AsyncSession,
        context_wrapper: ContextWrapper,
        model_class: type[T],
        rbac_filter_service: RbacFilterService | None = None,
        processor_executor: ProcessorExecutor | None = None,
        processor_executor_classes: list[BaseProcessor] | None = None,
    ) -> None:
        super().__init__()
        self.context = context_wrapper.get()
        self.auth_info = self.context.auth_info
        self.session = session
        self.model_class = model_class
        self._rbac_filter_service = rbac_filter_service
        self._processor_executor = processor_executor
        self._processor_executor_classes = processor_executor_classes or []

    async def _run_processors(
        self,
        event: RepositoryEvent,
        entity: T,
        original_entity: T | None = None,
    ) -> None:
        if not self._processor_executor:
            return
        context = EntityContext(
            entity=entity,
            entity_id=entity.id,
            event=event,
            original_entity=original_entity,
        )
        await self._processor_executor.execute(
            context, self._processor_executor_classes
        )

    def get_rbac_filter_strategy(self) -> RbacFilterStrategy | None:
        return None

    def compute_user_ids(self, entity: T) -> list[UUID] | None:
        """
        Override in subclasses to compute user_ids for an entity.

        Default: returns [created_by_id] if entity has both user_ids and created_by_id.
        Return None to skip setting user_ids.
        """
        if hasattr(entity, "user_ids"):
            return [self.auth_info.flow_user_id]
        return None

    async def execute(
        self,
        stmt: Select[GenQuery],  # pyright: ignore[reportInvalidTypeArguments]
        privilege: RbacPrivilegeTypeEnum = RbacPrivilegeTypeEnum.VIEW,
    ) -> Result[GenQuery]:  # pyright: ignore[reportInvalidTypeArguments]
        """
        Apply RBAC filtering to a select statement.

        Uses the repository's filter strategy if defined.
        Returns the original statement if no strategy is configured.
        """
        strategy = self.get_rbac_filter_strategy()

        if strategy and self._rbac_filter_service:
            stmt = await self._rbac_filter_service.apply_filter(
                stmt,
                strategy,
                self.context.auth_info.flow_user_id,
                self.context.auth_info.roles,
                privilege,
            )
        return await self.session.execute(stmt)

    async def get_edit(
        self,
        *,
        pk: uuid.UUID,
        options: list[ExecutableOption] | None = None,
        unique: bool = False,
        privilege: RbacPrivilegeTypeEnum = RbacPrivilegeTypeEnum.WRITE,
    ) -> T:
        stmt = select(self.model_class).where(self.model_class.id == pk)
        if options:
            stmt = stmt.options(*options)

        result = await self.execute(stmt, privilege)
        if unique:
            entity = result.unique().scalar_one_or_none()
        else:
            entity = result.scalars().one_or_none()

        if entity is None:
            raise UnauthorizedError(
                f"Access denied for {self.model_class.__name__} with id {pk}"
            )

        return entity

    async def get_by_id(
        self, entity_id: UUID | str, options: list[ExecutableOption] | None = None
    ) -> T:
        """
        Get an entity by its ID.

        Args:
            entity_id: The entity ID (UUID or string)

        Returns:
            The entity if found, None otherwise
        """
        if isinstance(entity_id, str):
            entity_id = UUID(entity_id)
        stmt = select(self.model_class).where(self.model_class.id == entity_id)

        if options:
            stmt = stmt.options(*options)
        result = await self.execute(
            stmt,
        )
        return result.unique().scalar_one()

    async def list_all(self, limit: int | None = None, offset: int = 0) -> list[T]:
        """
        List all entities with optional pagination.

        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entities
        """
        query = select(self.model_class).offset(offset)
        if limit is not None:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def prepare_create(self, entity: T) -> T:
        if hasattr(entity, "created_by_id"):
            setattr(entity, "created_by_id", self.context.auth_info.flow_user_id)

        if hasattr(entity, "created_at"):
            setattr(entity, "created_at", pendulum.now())

        user_ids = self.compute_user_ids(entity)
        if user_ids is not None and hasattr(entity, "user_ids"):
            setattr(entity, "user_ids", user_ids)

        await self._run_processors(RepositoryEvent.PRE_CREATE, entity)

        return entity

    async def create(self, entity: T) -> T:
        entity = await self.prepare_create(entity)
        self.session.add(entity)
        await self.session.flush()

        await self._run_processors(RepositoryEvent.POST_CREATE, entity)

        return entity

    async def update(self, incoming_entity: T) -> T:
        original_entity = await self.get_edit(pk=incoming_entity.id)

        init_fields = original_entity.get_init_fields()

        for column in incoming_entity.__table__.columns:
            if column.name in init_fields:
                setattr(
                    incoming_entity, column.name, getattr(original_entity, column.name)
                )

        user_ids = self.compute_user_ids(incoming_entity)
        if user_ids is not None and hasattr(incoming_entity, "user_ids"):
            setattr(incoming_entity, "user_ids", user_ids)

        await self._run_processors(
            RepositoryEvent.PRE_UPDATE, incoming_entity, original_entity
        )

        merged = await self.session.merge(incoming_entity)
        await self.session.flush()
        await self._run_processors(RepositoryEvent.POST_UPDATE, merged, original_entity)

        return merged

    async def delete(self, entity_id: UUID | str) -> bool:
        try:
            if isinstance(entity_id, str):
                entity_id = UUID(entity_id)

            entity = await self.get_edit(
                pk=entity_id, privilege=RbacPrivilegeTypeEnum.DELETE
            )

            await self._run_processors(RepositoryEvent.PRE_DELETE, entity)

            await self.session.delete(entity)
            await self.session.flush()

            await self._run_processors(RepositoryEvent.POST_DELETE, entity)

            return True
        except Exception as e:
            logger.exception(f"Deletion failed: {e}")
            raise DeletionError(
                f"Can not delete {self.model_class.__name__} as it is linked to other records"
            )

    async def exists(self, entity_id: UUID | str) -> bool:
        """
        Check if an entity exists.

        Args:
            entity_id: The entity ID

        Returns:
            True if exists, False otherwise
        """
        if isinstance(entity_id, str):
            entity_id = UUID(entity_id)

        result = await self.session.execute(
            select(func.count())
            .select_from(self.model_class)
            .where(self.model_class.id == entity_id)
        )
        return result.scalar_one() > 0

    async def count(self) -> int:
        """
        Count total number of entities.

        Returns:
            Total count
        """
        result = await self.session.execute(
            select(func.count()).select_from(self.model_class)
        )
        return result.scalar_one()

    async def bulk_create(self, entities: list[T]) -> list[T]:
        if not entities:
            return []

        for entity in entities:
            if hasattr(entity, "created_by_id"):
                setattr(entity, "created_by_id", self.context.auth_info.flow_user_id)

            if hasattr(entity, "created_at"):
                setattr(entity, "created_at", pendulum.now())

            user_ids = self.compute_user_ids(entity)
            if user_ids is not None and hasattr(entity, "user_ids"):
                setattr(entity, "user_ids", user_ids)

            await self._run_processors(RepositoryEvent.PRE_CREATE, entity)

        self.session.add_all(entities)
        await self.session.flush()

        for entity in entities:
            await self._run_processors(RepositoryEvent.POST_CREATE, entity)

        return entities

    async def find_by_entity(self, entity_type: EntityType, entity_id: UUID) -> list[T]:
        """
        Find all entities of this type linked to a specific entity via link relations.

        Requires the repository to define an `entity_type` class attribute.

        Args:
            entity_type: The type of entity to find links for
            entity_id: The ID of the entity

        Returns:
            List of entities linked to the specified entity

        Raises:
            ValueError: If entity_type class attribute is not defined
        """
        if self.entity_type is None:
            raise ValueError(
                f"{self.__class__.__name__} must define an entity_type class attribute "
                "to use find_by_entity"
            )

        stmt = select(self.model_class).join(
            LinkRelation,
            or_(
                (
                    (LinkRelation.source_entity_type == self.entity_type)
                    & (LinkRelation.target_entity_type == entity_type)
                    & (LinkRelation.target_entity_id == entity_id)
                    & (LinkRelation.source_entity_id == self.model_class.id)
                ),
                (
                    (LinkRelation.source_entity_type == entity_type)
                    & (LinkRelation.target_entity_type == self.entity_type)
                    & (LinkRelation.source_entity_id == entity_id)
                    & (LinkRelation.target_entity_id == self.model_class.id)
                ),
            ),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
