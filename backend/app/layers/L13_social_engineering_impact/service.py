"""Layer 13: Business logic for social and engineering impact."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.layers.L13_social_engineering_impact.models import (
    ImpactAssessment,
    Survey,
    SurveyResponse as SurveyResponseModel,
)
from app.layers.L13_social_engineering_impact.schemas import SurveyResponseCreate
from app.shared.exceptions import NotFoundError


async def list_assessments(db: AsyncSession) -> list[ImpactAssessment]:
    result = await db.execute(
        select(ImpactAssessment).order_by(ImpactAssessment.risk_level.desc())
    )
    return list(result.scalars().all())


async def list_surveys(db: AsyncSession) -> list[Survey]:
    result = await db.execute(select(Survey).order_by(Survey.created_at.desc()))
    return list(result.scalars().all())


async def submit_survey_response(
    db: AsyncSession, data: SurveyResponseCreate, user_id: uuid.UUID
) -> SurveyResponseModel:
    survey = await db.get(Survey, data.survey_id)
    if not survey:
        raise NotFoundError("Survey", str(data.survey_id))

    response = SurveyResponseModel(
        survey_id=data.survey_id,
        user_id=user_id,
        responses=data.responses,
    )
    db.add(response)
    await db.flush()
    return response
