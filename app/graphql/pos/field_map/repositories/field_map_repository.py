import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from app.core.db.transient_session import TenantSession
from app.graphql.pos.field_map.models.field_map import FieldMap, FieldMapField
from app.graphql.pos.field_map.models.field_map_enums import (
    FieldMapDirection,
    FieldMapType,
)


class FieldMapRepository:
    def __init__(self, session: TenantSession) -> None:
        self.session = session

    async def create(self, field_map: FieldMap) -> FieldMap:
        self.session.add(field_map)
        await self.session.flush([field_map])
        return field_map

    async def get_by_org_and_type(
        self,
        organization_id: uuid.UUID | None,
        map_type: FieldMapType,
        direction: FieldMapDirection = FieldMapDirection.SEND,
    ) -> FieldMap | None:
        if organization_id is None:
            stmt = (
                select(FieldMap)
                .where(FieldMap.organization_id.is_(None))
                .where(FieldMap.map_type == map_type.value)
                .where(FieldMap.direction == direction.value)
                .options(joinedload(FieldMap.fields))
            )
        else:
            stmt = (
                select(FieldMap)
                .where(FieldMap.organization_id == organization_id)
                .where(FieldMap.map_type == map_type.value)
                .where(FieldMap.direction == direction.value)
                .options(joinedload(FieldMap.fields))
            )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def add_field(self, field: FieldMapField) -> FieldMapField:
        self.session.add(field)
        await self.session.flush([field])
        return field

    async def add_fields(self, fields: list[FieldMapField]) -> list[FieldMapField]:
        for field in fields:
            self.session.add(field)
        await self.session.flush(fields)
        return fields

    async def update_field(self, field: FieldMapField) -> FieldMapField:
        await self.session.flush([field])
        return field

    async def delete_field(self, field_id: uuid.UUID) -> bool:
        stmt = delete(FieldMapField).where(FieldMapField.id == field_id)
        result: Any = await self.session.execute(stmt)
        return result.rowcount > 0

    async def get_field_by_id(self, field_id: uuid.UUID) -> FieldMapField | None:
        stmt = select(FieldMapField).where(FieldMapField.id == field_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
