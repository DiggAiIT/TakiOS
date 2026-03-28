"""Layer 12: API endpoints for quality management."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_db
from app.layers.L12_quality_management import service
from app.layers.L12_quality_management.schemas import (
    QualityDashboardResponse,
    QualityMetricResponse,
    UserFeedbackCreate,
    UserFeedbackResponse,
)

router = APIRouter()


@router.get("/metrics", response_model=list[QualityMetricResponse])
async def list_metrics(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all quality metrics."""
    del user
    return await service.list_metrics(db)


@router.get("/dashboard", response_model=QualityDashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get quality dashboard with latest measurements and feedback summary."""
    del user
    return await service.get_dashboard(db)


@router.post("/feedback", response_model=UserFeedbackResponse, status_code=201)
async def submit_feedback(
    data: UserFeedbackCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit quality feedback (e.g., bug, suggestion)."""
    return await service.create_feedback(db, data, user.id)


@router.get("/templates")
async def get_quality_templates():
    """Get standard quality templates for Software Medical Devices (IEC 62304, 62366)."""
    from app.layers.L12_quality_management.templates import SOFTWARE_COMPLIANCE_TEMPLATES
    return {"templates": SOFTWARE_COMPLIANCE_TEMPLATES}
