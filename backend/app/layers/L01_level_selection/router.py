"""Layer 1: API endpoints for knowledge pyramid and level selection."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_db
from app.layers.L01_level_selection import service
from app.layers.L01_level_selection.schemas import KnowledgeLevelResponse, PyramidResponse

router = APIRouter()


@router.get("/", response_model=list[KnowledgeLevelResponse])
async def list_levels(db: AsyncSession = Depends(get_db)):
    """List all knowledge pyramid levels."""
    return await service.get_all_levels(db)


@router.get("/pyramid", response_model=PyramidResponse)
async def get_pyramid(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the full pyramid structure with current user's progress."""
    levels = await service.get_all_levels(db)
    progress = await service.get_user_progress(db, user.id)
    return PyramidResponse(levels=levels, progress=progress)
