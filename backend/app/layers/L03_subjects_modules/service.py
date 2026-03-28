"""Layer 3: Business logic for subjects and modules."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.layers.L03_subjects_modules.models import Module, ModuleUnit, Subject
from app.shared.exceptions import NotFoundError


async def get_all_subjects(db: AsyncSession) -> list[Subject]:
    result = await db.execute(select(Subject).order_by(Subject.name_de))
    return list(result.scalars().all())


async def get_modules_by_subject(db: AsyncSession, subject_id: uuid.UUID) -> list[Module]:
    result = await db.execute(
        select(Module)
        .where(Module.subject_id == subject_id)
        .order_by(Module.semester, Module.code)
    )
    return list(result.scalars().all())


async def get_module_detail(db: AsyncSession, module_id: uuid.UUID) -> Module:
    result = await db.execute(
        select(Module)
        .where(Module.id == module_id)
        .options(selectinload(Module.units))
    )
    module = result.scalar_one_or_none()
    if not module:
        raise NotFoundError("Module", str(module_id))
    return module


async def get_all_modules(db: AsyncSession, semester: int | None = None) -> list[Module]:
    query = select(Module).order_by(Module.semester, Module.code)
    if semester is not None:
        query = query.where(Module.semester == semester)
    result = await db.execute(query)
    return list(result.scalars().all())
