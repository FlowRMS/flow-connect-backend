"""Base repository with common CRUD operations for all entities."""

from typing import Any, Generic, TypeVar
from uuid import UUID

import pendulum
from sqlalchemy import delete as sql_delete
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context_wrapper import ContextWrapper

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Base repository providing common CRUD operations.

    Type parameter T should be the SQLAlchemy model class.
    """

    def __init__(
        self,
        session: AsyncSession,
        context_wrapper: ContextWrapper,
        model_class: type[T],
    ) -> None:
        """
        Initialize the repository.

        Args:
            session: SQLAlchemy async session
            model_class: The SQLAlchemy model class this repository manages
        """
        super().__init__()
        self.context = context_wrapper.get()
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, entity_id: UUID | str) -> T | None:
        """
        Get an entity by its ID.

        Args:
            entity_id: The entity ID (UUID or string)

        Returns:
            The entity if found, None otherwise
        """
        if isinstance(entity_id, str):
            entity_id = UUID(entity_id)

        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == entity_id)
        )
        return result.scalar_one_or_none()

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

    async def create(self, entity: T) -> T:
        """
        Create a new entity.

        Args:
            entity: The entity to create

        Returns:
            The created entity
        """

        if hasattr(entity, "created_by"):
            setattr(entity, "created_by", self.context.auth_info.user_id)

        if hasattr(entity, "created_at"):
            setattr(entity, "created_at", pendulum.now())

        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        """
        Update an existing entity.

        Args:
            entity: The entity to update

        Returns:
            The updated entity
        """
        merged = await self.session.merge(entity)
        await self.session.flush()
        await self.session.refresh(merged)
        return merged

    async def delete(self, entity_id: UUID | str) -> bool:
        """
        Delete an entity by its ID.

        Args:
            entity_id: The entity ID

        Returns:
            True if deleted, False if not found
        """
        entity = await self.get_by_id(entity_id)
        if not entity:
            return False
        
        await self.session.delete(entity)
        await self.session.flush()
        return True

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
        """
        Create multiple entities in bulk.

        Args:
            entities: List of entities to create

        Returns:
            List of created entities
        """
        self.session.add_all(entities)
        await self.session.flush()
        for entity in entities:
            await self.session.refresh(entity)
        return entities
