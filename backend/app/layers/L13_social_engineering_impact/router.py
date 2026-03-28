"""Layer 13: API endpoints for social and engineering impact."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_db
from app.layers.L13_social_engineering_impact import service
from app.layers.L13_social_engineering_impact.schemas import (
    ImpactAssessmentResponse,
    SurveyResponse,
    SurveyResponseCreate,
    SurveyResponseOut,
)

router = APIRouter()


@router.get("/assessments", response_model=list[ImpactAssessmentResponse])
async def list_assessments(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all impact assessments."""
    del user
    return await service.list_assessments(db)


@router.get("/surveys", response_model=list[SurveyResponse])
async def list_surveys(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all surveys."""
    del user
    return await service.list_surveys(db)


@router.post("/surveys/respond", response_model=SurveyResponseOut, status_code=201)
async def submit_survey_response(
    data: SurveyResponseCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit a response to a survey."""
    return await service.submit_survey_response(db, data, user.id)
