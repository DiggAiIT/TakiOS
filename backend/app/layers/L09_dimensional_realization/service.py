"""Layer 9: Business logic for stage gate workflow."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.layers.L09_dimensional_realization.models import (
    ProjectRealization,
    RealizationStage,
    StageGateCriteria,
)
from app.layers.L09_dimensional_realization.schemas import AdvanceStageRequest
from app.shared.exceptions import NotFoundError


async def list_criteria(db: AsyncSession) -> list[StageGateCriteria]:
    result = await db.execute(select(StageGateCriteria).order_by(StageGateCriteria.stage))
    return list(result.scalars().all())


async def get_criteria_for_stage(
    db: AsyncSession, stage: RealizationStage
) -> StageGateCriteria:
    result = await db.execute(
        select(StageGateCriteria).where(StageGateCriteria.stage == stage)
    )
    criteria = result.scalar_one_or_none()
    if not criteria:
        raise NotFoundError("StageGateCriteria", stage.value)
    return criteria


async def advance_stage(
    db: AsyncSession, data: AdvanceStageRequest, user_id: uuid.UUID
) -> ProjectRealization:
    realization = ProjectRealization(
        project_id=data.project_id,
        stage=data.target_stage,
        evidence=data.evidence,
        approved_by=user_id,
    )
    db.add(realization)
    await db.flush()
    return realization
