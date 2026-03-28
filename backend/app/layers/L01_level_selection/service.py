"""Layer 1: Business logic for knowledge pyramid and level selection."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.layers.L01_level_selection.models import (
    KnowledgeLevel,
    LevelStatus,
    UserLevelProgress,
)


async def get_all_levels(db: AsyncSession) -> list[KnowledgeLevel]:
    result = await db.execute(
        select(KnowledgeLevel).order_by(KnowledgeLevel.pyramid_position)
    )
    return list(result.scalars().all())


async def get_user_progress(
    db: AsyncSession, user_id: uuid.UUID
) -> dict[str, LevelStatus]:
    result = await db.execute(
        select(UserLevelProgress).where(UserLevelProgress.user_id == user_id)
    )
    return {
        str(p.level_id): p.status for p in result.scalars().all()
    }


async def update_level_status(
    db: AsyncSession, user_id: uuid.UUID, level_id: uuid.UUID, status: LevelStatus
) -> UserLevelProgress:
    result = await db.execute(
        select(UserLevelProgress).where(
            UserLevelProgress.user_id == user_id,
            UserLevelProgress.level_id == level_id,
        )
    )
    progress = result.scalar_one_or_none()
    if progress:
        progress.status = status
    else:
        progress = UserLevelProgress(user_id=user_id, level_id=level_id, status=status)
        db.add(progress)
    await db.flush()
    return progress


async def handle_exam_completed(payload: dict) -> None:
    """React to exam completion: update pyramid level progress.

    When a user passes an exam, find which pyramid levels include that
    module in their unlock_criteria, then mark the level as in_progress
    or completed accordingly.
    """
    db: AsyncSession = payload["db"]
    user_id = uuid.UUID(payload["user_id"])
    exam_id = uuid.UUID(payload["exam_id"])
    passed = payload.get("passed", False)

    if not passed:
        return

    # Cross-layer imports (acceptable in event handlers)
    from app.layers.L05_knowledge_assessment.models import Exam, ExamAttempt
    from app.layers.L03_subjects_modules.models import Module

    exam = await db.get(Exam, exam_id)
    if not exam:
        return
    module = await db.get(Module, exam.module_id)
    if not module:
        return

    levels = await get_all_levels(db)
    for level in levels:
        criteria = level.unlock_criteria
        if not criteria or "required_module_codes" not in criteria:
            continue

        required_codes: list[str] = criteria["required_module_codes"]
        if module.code not in required_codes:
            continue

        # Check whether ALL required modules have been passed by this user
        all_passed = True
        for code in required_codes:
            mod_result = await db.execute(
                select(Module).where(Module.code == code)
            )
            req_module = mod_result.scalar_one_or_none()
            if not req_module:
                all_passed = False
                continue

            attempt_result = await db.execute(
                select(ExamAttempt)
                .join(Exam, ExamAttempt.exam_id == Exam.id)
                .where(
                    Exam.module_id == req_module.id,
                    ExamAttempt.user_id == user_id,
                    ExamAttempt.passed == True,  # noqa: E712
                )
                .limit(1)
            )
            if not attempt_result.scalar_one_or_none():
                all_passed = False
                break

        if all_passed:
            await update_level_status(db, user_id, level.id, LevelStatus.COMPLETED)
        else:
            progress = await get_user_progress(db, user_id)
            current = progress.get(str(level.id), LevelStatus.LOCKED)
            if current == LevelStatus.LOCKED:
                await update_level_status(db, user_id, level.id, LevelStatus.IN_PROGRESS)
