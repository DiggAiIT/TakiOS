"""Layer 3: API endpoints for subjects and modules."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.layers.L03_subjects_modules import service
from app.layers.L03_subjects_modules.schemas import (
    ModuleDetailResponse,
    ModuleResponse,
    SubjectResponse,
)

router = APIRouter()


@router.get("/", response_model=list[SubjectResponse])
async def list_subjects(db: AsyncSession = Depends(get_db)):
    """List all academic subjects."""
    return await service.get_all_subjects(db)


@router.get("/{subject_id}/modules", response_model=list[ModuleResponse])
async def list_modules_by_subject(
    subject_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """List modules for a specific subject."""
    return await service.get_modules_by_subject(db, subject_id)


@router.get("/modules", response_model=list[ModuleResponse])
async def list_all_modules(
    semester: int | None = Query(None, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
):
    """List all modules, optionally filtered by semester."""
    return await service.get_all_modules(db, semester)


@router.get("/modules/{module_id}", response_model=ModuleDetailResponse)
async def get_module(module_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get detailed module information with learning units."""
    return await service.get_module_detail(db, module_id)
