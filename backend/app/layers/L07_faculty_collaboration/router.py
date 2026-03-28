"""Layer 7: API endpoints for faculty collaboration."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_db
from app.layers.L07_faculty_collaboration import service
from app.layers.L07_faculty_collaboration.schemas import (
    FacultyProfileCreate,
    FacultyProfileResponse,
    FacultyProfileUpdate,
    ReviewRequestCreate,
    ReviewRequestResponse,
    SubmitReviewRequest,
)

router = APIRouter()


# ── Faculty Profiles ────────────────────────────────────────────────


@router.get("/faculty", response_model=list[FacultyProfileResponse])
async def list_faculty(db: AsyncSession = Depends(get_db)):
    """List available faculty for review."""
    return await service.get_available_faculty(db)


@router.post("/faculty/profile", response_model=FacultyProfileResponse, status_code=201)
async def create_profile(
    data: FacultyProfileCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a faculty profile for the current user."""
    return await service.create_faculty_profile(db, user.id, data)


@router.get("/faculty/profile", response_model=FacultyProfileResponse)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get the current user's faculty profile."""
    profile = await service.get_faculty_profile(db, user.id)
    if not profile:
        from app.shared.exceptions import NotFoundError
        raise NotFoundError("FacultyProfile", str(user.id))
    return profile


@router.patch("/faculty/profile", response_model=FacultyProfileResponse)
async def update_profile(
    data: FacultyProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update the current user's faculty profile."""
    return await service.update_faculty_profile(db, user.id, data)


# ── Review Requests ─────────────────────────────────────────────────


@router.post("/reviews", response_model=ReviewRequestResponse, status_code=201)
async def request_review(
    data: ReviewRequestCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Request a faculty review for a project."""
    return await service.create_review_request(db, data.project_id, data.faculty_id, user.id)


@router.get("/reviews/incoming", response_model=list[ReviewRequestResponse])
async def list_incoming_reviews(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List review requests assigned to the current faculty user."""
    profile = await service.get_faculty_profile(db, user.id)
    if not profile:
        return []
    return await service.get_reviews_for_faculty(db, profile.id)


@router.get("/reviews/project/{project_id}", response_model=list[ReviewRequestResponse])
async def list_project_reviews(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List review requests for a specific project."""
    return await service.get_project_reviews_for_user(db, project_id, user.id)


@router.post("/reviews/{review_id}/accept", response_model=ReviewRequestResponse)
async def accept_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Accept a review request (faculty only)."""
    return await service.accept_review(db, review_id, user.id)


@router.post("/reviews/{review_id}/decline", response_model=ReviewRequestResponse)
async def decline_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Decline a review request (faculty only)."""
    return await service.decline_review(db, review_id, user.id)


@router.post("/reviews/{review_id}/complete", response_model=ReviewRequestResponse)
async def complete_review(
    review_id: uuid.UUID,
    data: SubmitReviewRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit faculty review feedback and mark as complete."""
    return await service.complete_review(db, review_id, data.review_text, user.id)
