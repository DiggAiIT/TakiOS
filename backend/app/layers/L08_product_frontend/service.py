"""Layer 8: Business logic for frontend preferences."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.layers.L08_product_frontend.models import UserPreference
from app.layers.L08_product_frontend.schemas import UserPreferenceUpdate


async def get_preferences(db: AsyncSession, user_id: uuid.UUID) -> UserPreference:
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == user_id)
    )
    prefs = result.scalar_one_or_none()
    if not prefs:
        prefs = UserPreference(user_id=user_id)
        db.add(prefs)
        await db.flush()
    return prefs


async def update_preferences(
    db: AsyncSession, user_id: uuid.UUID, data: UserPreferenceUpdate
) -> UserPreference:
    prefs = await get_preferences(db, user_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(prefs, field, value)
    await db.flush()
    return prefs
