"""Layer 6: Business logic for project creation and management."""

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.layers.L06_project_creation.models import (
    Project,
    ProjectArtifact,
    ProjectMilestone,
)
from app.layers.L06_project_creation.schemas import (
    MilestoneCreate,
    MilestoneUpdate,
    ProjectCreate,
    ProjectUpdate,
)
from app.shared.exceptions import ForbiddenError, NotFoundError


# ── Projects ────────────────────────────────────────────────────────


async def create_project(db: AsyncSession, data: ProjectCreate, user_id: uuid.UUID) -> Project:
    project = Project(
        title=data.title,
        description=data.description,
        module_id=data.module_id,
        created_by=user_id,
    )
    db.add(project)
    await db.flush()
    return project


async def get_user_projects(db: AsyncSession, user_id: uuid.UUID) -> list[Project]:
    result = await db.execute(
        select(Project).where(Project.created_by == user_id).order_by(Project.created_at.desc())
    )
    return list(result.scalars().all())


async def get_project(db: AsyncSession, project_id: uuid.UUID, user_id: uuid.UUID | None = None) -> Project:
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .options(selectinload(Project.milestones), selectinload(Project.artifacts))
    )
    project = result.scalar_one_or_none()
    if not project:
        raise NotFoundError("Project", str(project_id))
    if user_id is not None and project.created_by != user_id:
        raise ForbiddenError("Only the project owner can access this project")
    return project


async def update_project(
    db: AsyncSession, project_id: uuid.UUID, data: ProjectUpdate, user_id: uuid.UUID
) -> Project:
    project = await get_project(db, project_id, user_id)
    if data.title is not None:
        project.title = data.title
    if data.description is not None:
        project.description = data.description
    if data.status is not None:
        project.status = data.status
    if data.realization_stage is not None:
        project.realization_stage = data.realization_stage
    await db.flush()
    return project


# ── Milestones ──────────────────────────────────────────────────────


async def add_milestone(
    db: AsyncSession, project_id: uuid.UUID, data: MilestoneCreate, user_id: uuid.UUID
) -> ProjectMilestone:
    await get_project(db, project_id, user_id)
    # Auto-assign position as next in sequence
    count_result = await db.execute(
        select(func.count()).where(ProjectMilestone.project_id == project_id)
    )
    next_pos = (count_result.scalar() or 0) + 1
    milestone = ProjectMilestone(
        project_id=project_id,
        title=data.title,
        description=data.description,
        position=next_pos,
    )
    db.add(milestone)
    await db.flush()
    return milestone


async def update_milestone(
    db: AsyncSession, milestone_id: uuid.UUID, data: MilestoneUpdate, user_id: uuid.UUID
) -> ProjectMilestone:
    milestone = await db.get(ProjectMilestone, milestone_id)
    if not milestone:
        raise NotFoundError("Milestone", str(milestone_id))
    project = await db.get(Project, milestone.project_id)
    if not project or project.created_by != user_id:
        raise ForbiddenError("Only the project owner can update milestones")
    if data.title is not None:
        milestone.title = data.title
    if data.description is not None:
        milestone.description = data.description
    if data.completed is not None:
        milestone.completed = data.completed
    await db.flush()
    return milestone


async def delete_milestone(db: AsyncSession, milestone_id: uuid.UUID, user_id: uuid.UUID) -> None:
    milestone = await db.get(ProjectMilestone, milestone_id)
    if not milestone:
        raise NotFoundError("Milestone", str(milestone_id))
    project = await db.get(Project, milestone.project_id)
    if not project or project.created_by != user_id:
        raise ForbiddenError("Only the project owner can delete milestones")
    await db.delete(milestone)
    await db.flush()


# ── Artifacts ───────────────────────────────────────────────────────


async def add_artifact(
    db: AsyncSession,
    project_id: uuid.UUID,
    file_url: str,
    file_type: str,
    user_id: uuid.UUID,
) -> ProjectArtifact:
    await get_project(db, project_id, user_id)
    artifact = ProjectArtifact(
        project_id=project_id,
        file_url=file_url,
        file_type=file_type,
        uploaded_by=user_id,
    )
    db.add(artifact)
    await db.flush()
    return artifact


async def delete_artifact(db: AsyncSession, artifact_id: uuid.UUID, user_id: uuid.UUID) -> ProjectArtifact:
    artifact = await db.get(ProjectArtifact, artifact_id)
    if not artifact:
        raise NotFoundError("Artifact", str(artifact_id))
    await get_project(db, artifact.project_id, user_id)
    await db.delete(artifact)
    await db.flush()
    return artifact
