"""Layer 12: Business logic for quality management."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.layers.L12_quality_management.models import QualityMeasurement, QualityMetric, UserFeedback
from app.layers.L12_quality_management.schemas import (
    QualityDashboardMetric,
    QualityDashboardResponse,
    UserFeedbackCreate,
)


async def list_metrics(db: AsyncSession) -> list[QualityMetric]:
    result = await db.execute(select(QualityMetric).order_by(QualityMetric.name))
    return list(result.scalars().all())


async def get_dashboard(db: AsyncSession) -> QualityDashboardResponse:
    metrics = await list_metrics(db)
    dashboard_metrics: list[QualityDashboardMetric] = []

    for metric in metrics:
        latest = await db.execute(
            select(QualityMeasurement.measured_value)
            .where(QualityMeasurement.metric_id == metric.id)
            .order_by(QualityMeasurement.measured_at.desc())
            .limit(1)
        )
        latest_value = latest.scalar_one_or_none()
        dashboard_metrics.append(
            QualityDashboardMetric(
                metric_id=metric.id,
                name=metric.name,
                target_value=metric.target_value,
                latest_value=latest_value,
                unit=metric.unit,
            )
        )

    feedback_count = await db.execute(select(func.count(UserFeedback.id)))
    avg_rating = await db.execute(select(func.avg(UserFeedback.rating)))

    return QualityDashboardResponse(
        metrics=dashboard_metrics,
        total_feedback_count=feedback_count.scalar() or 0,
        average_rating=round(float(avg_rating.scalar() or 0), 2) or None,
    )


async def create_feedback(
    db: AsyncSession, data: UserFeedbackCreate, user_id: uuid.UUID
) -> UserFeedback:
    feedback = UserFeedback(
        user_id=user_id,
        category=data.category,
        text=data.text,
        rating=data.rating,
    )
    db.add(feedback)
    await db.flush()
    return feedback
