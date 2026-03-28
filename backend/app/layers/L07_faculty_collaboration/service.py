"""Layer 7: Business logic for faculty collaboration."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.layers.L06_project_creation.models import Project
from app.layers.L07_faculty_collaboration.models import (
    FacultyProfile,
    ReviewRequest,
    ReviewStatus,
)
from app.layers.L07_faculty_collaboration.schemas import (
    FacultyProfileCreate,
    FacultyProfileUpdate,
)
from app.shared.exceptions import ConflictError, ForbiddenError, NotFoundError


# ── Faculty Profiles ────────────────────────────────────────────────


async def get_available_faculty(db: AsyncSession) -> list[FacultyProfile]:
    result = await db.execute(
        select(FacultyProfile).where(FacultyProfile.available_for_review.is_(True))
    )
    return list(result.scalars().all())


async def get_faculty_profile(db: AsyncSession, user_id: uuid.UUID) -> FacultyProfile | None:
    result = await db.execute(
        select(FacultyProfile).where(FacultyProfile.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_faculty_profile(
    db: AsyncSession, user_id: uuid.UUID, data: FacultyProfileCreate
) -> FacultyProfile:
    existing = await get_faculty_profile(db, user_id)
    if existing:
        raise ConflictError("Faculty profile already exists for this user")
    profile = FacultyProfile(
        user_id=user_id,
        department=data.department,
        expertise_areas={"areas": data.expertise_areas},
    )
    db.add(profile)
    await db.flush()
    return profile


async def update_faculty_profile(
    db: AsyncSession, user_id: uuid.UUID, data: FacultyProfileUpdate
) -> FacultyProfile:
    profile = await get_faculty_profile(db, user_id)
    if not profile:
        raise NotFoundError("FacultyProfile", str(user_id))
    if data.department is not None:
        profile.department = data.department
    if data.expertise_areas is not None:
        profile.expertise_areas = {"areas": data.expertise_areas}
    if data.available_for_review is not None:
        profile.available_for_review = data.available_for_review
    await db.flush()
    return profile


# ── Review Requests ─────────────────────────────────────────────────


async def create_review_request(
    db: AsyncSession, project_id: uuid.UUID, faculty_id: uuid.UUID, requested_by: uuid.UUID
) -> ReviewRequest:
    project = await db.get(Project, project_id)
    if not project:
        raise NotFoundError("Project", str(project_id))
    if project.created_by != requested_by:
        raise ForbiddenError("Only the project owner can request a faculty review")

    review = ReviewRequest(
        project_id=project_id, faculty_id=faculty_id, requested_by=requested_by
    )
    db.add(review)
    await db.flush()
    return review


async def get_reviews_for_faculty(db: AsyncSession, faculty_id: uuid.UUID) -> list[ReviewRequest]:
    result = await db.execute(
        select(ReviewRequest)
        .where(ReviewRequest.faculty_id == faculty_id)
        .order_by(ReviewRequest.created_at.desc())
    )
    return list(result.scalars().all())


async def get_reviews_for_project(db: AsyncSession, project_id: uuid.UUID) -> list[ReviewRequest]:
    result = await db.execute(
        select(ReviewRequest)
        .where(ReviewRequest.project_id == project_id)
        .order_by(ReviewRequest.created_at.desc())
    )
    return list(result.scalars().all())


async def get_project_reviews_for_user(
    db: AsyncSession, project_id: uuid.UUID, user_id: uuid.UUID
) -> list[ReviewRequest]:
    project = await db.get(Project, project_id)
    if not project:
        raise NotFoundError("Project", str(project_id))

    profile = await get_faculty_profile(db, user_id)
    if project.created_by != user_id and profile is None:
        raise ForbiddenError("Only the project owner or assigned faculty can view project reviews")

    reviews = await get_reviews_for_project(db, project_id)
    if project.created_by == user_id:
        return reviews
    if profile is None:
        return []
    return [review for review in reviews if review.faculty_id == profile.id]


async def accept_review(
    db: AsyncSession, review_id: uuid.UUID, faculty_user_id: uuid.UUID
) -> ReviewRequest:
    review = await db.get(ReviewRequest, review_id)
    if not review:
        raise NotFoundError("ReviewRequest", str(review_id))
    profile = await get_faculty_profile(db, faculty_user_id)
    if not profile or profile.id != review.faculty_id:
        raise ForbiddenError("Only the assigned faculty can accept this review")
    review.status = ReviewStatus.ACCEPTED
    await db.flush()
    return review


async def decline_review(
    db: AsyncSession, review_id: uuid.UUID, faculty_user_id: uuid.UUID
) -> ReviewRequest:
    review = await db.get(ReviewRequest, review_id)
    if not review:
        raise NotFoundError("ReviewRequest", str(review_id))
    profile = await get_faculty_profile(db, faculty_user_id)
    if not profile or profile.id != review.faculty_id:
        raise ForbiddenError("Only the assigned faculty can decline this review")
    review.status = ReviewStatus.DECLINED
    await db.flush()
    return review


async def complete_review(
    db: AsyncSession, review_id: uuid.UUID, review_text: str, faculty_user_id: uuid.UUID
) -> ReviewRequest:
    review = await db.get(ReviewRequest, review_id)
    if not review:
        raise NotFoundError("ReviewRequest", str(review_id))
    profile = await get_faculty_profile(db, faculty_user_id)
    if not profile or profile.id != review.faculty_id:
        raise ForbiddenError("Only the assigned faculty can complete this review")
    review.status = ReviewStatus.COMPLETED
    review.review_text = review_text
    await db.flush()
    return review
