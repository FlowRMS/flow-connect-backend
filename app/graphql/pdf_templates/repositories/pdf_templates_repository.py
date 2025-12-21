

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.context_wrapper import ContextWrapper
from app.graphql.base_repository import BaseRepository
from app.graphql.pdf_templates.models.pdf_template_model import PdfTemplate
from app.graphql.pdf_templates.models.pdf_template_module_model import PdfTemplateModule
from app.graphql.pdf_templates.models.pdf_template_type_model import PdfTemplateType


class PdfTemplatesRepository(BaseRepository[PdfTemplate]):

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, PdfTemplate)

    async def get_by_id_with_modules(self, template_id: str | UUID) -> PdfTemplate | None:
        stmt = (
            select(PdfTemplate)
            .where(PdfTemplate.id == str(template_id))
            .options(selectinload(PdfTemplate.modules))
            .options(selectinload(PdfTemplate.template_type))
            .options(selectinload(PdfTemplate.created_by))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_with_modules(
        self, limit: int = 1000, template_type_code: str | None = None,
        is_system: bool | None = None
    ) -> list[PdfTemplate]:
        stmt = (
            select(PdfTemplate)
            .options(selectinload(PdfTemplate.modules))
            .options(selectinload(PdfTemplate.template_type))
            .options(selectinload(PdfTemplate.created_by))
        )
        if template_type_code:
            stmt = stmt.where(PdfTemplate.template_type_code == template_type_code)
        if is_system is not None:
            stmt = stmt.where(PdfTemplate.is_system == is_system)
        stmt = stmt.limit(limit).order_by(PdfTemplate.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_system_templates(
        self, limit: int = 1000, template_type_code: str | None = None
    ) -> list[PdfTemplate]:

        return await self.get_all_with_modules(
            limit=limit, 
            template_type_code=template_type_code, 
            is_system=True
        )

    async def get_by_template_type_id(
        self, template_type_id: UUID, limit: int = 1000
    ) -> list[PdfTemplate]:
        stmt = (
            select(PdfTemplate)
            .where(PdfTemplate.template_type_id == template_type_id)
            .options(selectinload(PdfTemplate.modules))
            .options(selectinload(PdfTemplate.template_type))
            .options(selectinload(PdfTemplate.created_by))
            .limit(limit)
            .order_by(PdfTemplate.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_default_template(self, template_type_code: str) -> PdfTemplate | None:
        stmt = (
            select(PdfTemplate)
            .where(
                PdfTemplate.template_type_code == template_type_code,
                PdfTemplate.is_default == True,  
            )
            .options(selectinload(PdfTemplate.modules))
            .options(selectinload(PdfTemplate.template_type))
            .options(selectinload(PdfTemplate.created_by))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_name(
        self, search_term: str, limit: int = 20
    ) -> list[PdfTemplate]:
        stmt = (
            select(PdfTemplate)
            .where(PdfTemplate.name.ilike(f"%{search_term}%"))
            .options(selectinload(PdfTemplate.modules))
            .options(selectinload(PdfTemplate.template_type))
            .options(selectinload(PdfTemplate.created_by))
            .limit(limit)
            .order_by(PdfTemplate.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_module(self, module: PdfTemplateModule) -> PdfTemplateModule:
        self.session.add(module)
        await self.session.flush()
        await self.session.refresh(module)
        return module

    async def delete_modules_by_template_id(self, template_id: str | UUID) -> None:
        from uuid import UUID as UUIDType
        from sqlalchemy import delete
        if isinstance(template_id, str):
            template_id = UUIDType(template_id)
        stmt = delete(PdfTemplateModule).where(
            PdfTemplateModule.template_id == template_id
        )
        _ = await self.session.execute(stmt)
        await self.session.flush()

    async def unset_defaults_for_type(
        self, template_type_code: str, exclude_id: str | None = None
    ) -> None:
        from sqlalchemy import update
        stmt = (
            update(PdfTemplate)
            .where(
                PdfTemplate.template_type_code == template_type_code,
                PdfTemplate.is_default == True, 
            )
            .values(is_default=False)
        )
        if exclude_id:
            stmt = stmt.where(PdfTemplate.id != exclude_id)
        _ = await self.session.execute(stmt)
        await self.session.flush()


class PdfTemplateTypesRepository(BaseRepository[PdfTemplateType]):

    def __init__(self, context_wrapper: ContextWrapper, session: AsyncSession) -> None:
        super().__init__(session, context_wrapper, PdfTemplateType)

    async def get_all_ordered(self, limit: int = 1000) -> list[PdfTemplateType]:
        stmt = (
            select(PdfTemplateType)
            .limit(limit)
            .order_by(
                PdfTemplateType.display_order.asc().nulls_last(),
                PdfTemplateType.name.asc(),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def exists_with_display_order(
        self, display_order: int, exclude_id: UUID | None = None
    ) -> bool:

        stmt = select(PdfTemplateType).where(
            PdfTemplateType.display_order == display_order
        )
        if exclude_id:
            stmt = stmt.where(PdfTemplateType.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

