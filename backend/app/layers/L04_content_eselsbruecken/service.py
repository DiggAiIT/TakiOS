"""Layer 4: Business logic for content and Eselsbrücken generation.

This is the CORE INNOVATION of TakiOS — personalized mnemonic generation
using AI, tailored to each student's learning profile (Maßschneidung).
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.client import get_ai_client
from app.layers.L04_content_eselsbruecken.models import (
    Content,
    ContentVersion,
    LearningProfile,
    Mnemonic,
    MnemonicType,
)
from app.shared.exceptions import NotFoundError


async def get_content_for_unit(db: AsyncSession, module_unit_id: uuid.UUID) -> Content:
    result = await db.execute(
        select(Content).where(Content.module_unit_id == module_unit_id)
    )
    content = result.scalar_one_or_none()
    if not content:
        raise NotFoundError("Content", str(module_unit_id))
    return content


async def get_content_with_body(
    db: AsyncSession, module_unit_id: uuid.UUID
) -> tuple[Content, str]:
    """Get content for a unit with the current version's markdown body."""
    content = await get_content_for_unit(db, module_unit_id)
    body = ""
    if content.current_version_id:
        version_result = await db.execute(
            select(ContentVersion).where(ContentVersion.id == content.current_version_id)
        )
        version = version_result.scalar_one_or_none()
        if version:
            body = version.body_markdown
    return content, body


async def get_mnemonics_for_content(
    db: AsyncSession, content_id: uuid.UUID, user_id: uuid.UUID | None = None
) -> list[Mnemonic]:
    query = select(Mnemonic).where(Mnemonic.content_id == content_id)
    if user_id:
        # Return both shared (user_id=None) and personal mnemonics
        query = query.where((Mnemonic.user_id == user_id) | (Mnemonic.user_id.is_(None)))
    result = await db.execute(query)
    return list(result.scalars().all())


async def generate_mnemonic(
    db: AsyncSession,
    content_id: uuid.UUID,
    user_id: uuid.UUID,
    mnemonic_type: MnemonicType,
    language: str = "de",
    project_context: str | None = None,
) -> Mnemonic:
    """Generate a personalized Eselsbrücke using AI.

    This is the Maßschneidung: the mnemonic is tailored to the user's
    learning profile, cultural context, preferred mnemonic type, and their active project.
    """
    # Get the content
    result = await db.execute(select(Content).where(Content.id == content_id))
    content = result.scalar_one_or_none()
    if not content:
        raise NotFoundError("Content", str(content_id))

    # Get content body
    if content.current_version_id:
        version_result = await db.execute(
            select(ContentVersion).where(ContentVersion.id == content.current_version_id)
        )
        version = version_result.scalar_one_or_none()
        content_text = version.body_markdown if version else ""
    else:
        content_text = ""

    # Get user learning profile
    profile_result = await db.execute(
        select(LearningProfile).where(LearningProfile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()

    # Build AI prompt
    lang_name = "German" if language == "de" else "English"
    prompt = (
        f"Create a {mnemonic_type.value} mnemonic (Eselsbrücke) in {lang_name} "
        f"for the following learning content:\n\n{content_text}\n\n"
    )
    if project_context:
        prompt += f"The student is actively working on a project: '{project_context}'. Incorporate elements of this project into the mnemonic to make it directly relevant to their work.\n"

    if profile and profile.cultural_context:
        prompt += f"The student's cultural context: {profile.cultural_context}\n"
    prompt += (
        "The mnemonic should be memorable, accurate, and help the student "
        "anchor this knowledge specifically to their project if provided. Keep it concise."
    )

    system = (
        "You are TakiOS, a knowledge engineering system specializing in "
        "personalized learning. Create effective, culturally-aware mnemonics "
        "(Eselsbrücken) that help students retain biomedical engineering concepts."
    )

    ai_client = get_ai_client()
    mnemonic_text = await ai_client.generate_text(prompt=prompt, system=system, max_tokens=500)

    # Save to database
    mnemonic = Mnemonic(
        content_id=content_id,
        user_id=user_id,
        mnemonic_text=mnemonic_text,
        mnemonic_type=mnemonic_type,
        language=language,
        ai_generated=True,
    )
    db.add(mnemonic)
    await db.flush()
    return mnemonic


async def rate_mnemonic(
    db: AsyncSession, mnemonic_id: uuid.UUID, score: float
) -> Mnemonic:
    result = await db.execute(select(Mnemonic).where(Mnemonic.id == mnemonic_id))
    mnemonic = result.scalar_one_or_none()
    if not mnemonic:
        raise NotFoundError("Mnemonic", str(mnemonic_id))
    mnemonic.effectiveness_score = score
    await db.flush()
    return mnemonic
