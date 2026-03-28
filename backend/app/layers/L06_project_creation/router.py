"""Layer 6: API endpoints for project creation."""

import uuid

from fastapi import APIRouter, Depends, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.core.storage import delete_file, upload_file
from app.config import settings
from app.database import get_db
from app.layers.L06_project_creation import service
from app.layers.L06_project_creation.schemas import (
    ArtifactResponse,
    MilestoneCreate,
    MilestoneResponse,
    MilestoneUpdate,
    ProjectCreate,
    ProjectDetailResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.shared.exceptions import PayloadTooLargeError

router = APIRouter()


# ── Projects ────────────────────────────────────────────────────────


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create a new project."""
    return await service.create_project(db, data, user.id)


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List the current user's projects."""
    return await service.get_user_projects(db, user.id)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get project details with milestones and artifacts."""
    return await service.get_project(db, project_id, user.id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update project title, description, status, or realization stage."""
    return await service.update_project(db, project_id, data, user.id)


# ── Milestones ──────────────────────────────────────────────────────


@router.post("/{project_id}/milestones", response_model=MilestoneResponse, status_code=201)
async def add_milestone(
    project_id: uuid.UUID,
    data: MilestoneCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Add a milestone to a project."""
    return await service.add_milestone(db, project_id, data, user.id)


@router.patch("/milestones/{milestone_id}", response_model=MilestoneResponse)
async def update_milestone(
    milestone_id: uuid.UUID,
    data: MilestoneUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a milestone (title, description, or completion status)."""
    return await service.update_milestone(db, milestone_id, data, user.id)


@router.delete("/milestones/{milestone_id}", status_code=204)
async def delete_milestone(
    milestone_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a milestone."""
    await service.delete_milestone(db, milestone_id, user.id)


# ── Artifacts ───────────────────────────────────────────────────────


@router.post("/{project_id}/artifacts", response_model=ArtifactResponse, status_code=201)
async def upload_artifact(
    project_id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Upload a file artifact to a project."""
    file_data = await file.read()
    if len(file_data) > settings.max_artifact_upload_size_bytes:
        raise PayloadTooLargeError(
            f"Artifact exceeds {settings.max_artifact_upload_size_bytes} bytes"
        )
    key = f"projects/{project_id}/{file.filename}"
    await upload_file(key, file_data, file.content_type or "application/octet-stream")
    return await service.add_artifact(db, project_id, key, file.content_type or "unknown", user.id)


@router.delete("/artifacts/{artifact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_artifact(
    artifact_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a project artifact."""
    artifact = await service.delete_artifact(db, artifact_id, user.id)
    await delete_file(artifact.file_url)
