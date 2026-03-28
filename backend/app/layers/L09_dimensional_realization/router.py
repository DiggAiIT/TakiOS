"""Layer 9: API endpoints for dimensional realization."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_db
from app.layers.L09_dimensional_realization import service
from app.layers.L09_dimensional_realization.models import RealizationStage
from app.layers.L09_dimensional_realization.schemas import (
    AdvanceStageRequest,
    ProjectRealizationResponse,
    StageGateCriteriaResponse,
)

router = APIRouter()


@router.get("/criteria", response_model=list[StageGateCriteriaResponse])
async def list_criteria(db: AsyncSession = Depends(get_db)):
    """List all stage gate criteria."""
    return await service.list_criteria(db)


@router.get("/criteria/{stage}", response_model=StageGateCriteriaResponse)
async def get_criteria(stage: RealizationStage, db: AsyncSession = Depends(get_db)):
    """Get criteria for a specific stage."""
    return await service.get_criteria_for_stage(db, stage)


@router.post("/advance", response_model=ProjectRealizationResponse, status_code=201)
async def advance_stage(
    data: AdvanceStageRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Advance a project to the next realization stage."""
    return await service.advance_stage(db, data, user.id)
