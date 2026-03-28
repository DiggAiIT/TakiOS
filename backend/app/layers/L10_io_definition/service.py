"""Layer 10: Business logic for I/O capabilities and preferences."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.layers.L10_io_definition.models import IOCapability, UserIOPreference
from app.layers.L10_io_definition.schemas import UserIOPreferenceUpdate


async def list_capabilities(db: AsyncSession) -> list[IOCapability]:
    result = await db.execute(select(IOCapability).order_by(IOCapability.name))
    return list(result.scalars().all())


async def get_user_io_preferences(db: AsyncSession, user_id: uuid.UUID) -> UserIOPreference:
    result = await db.execute(
        select(UserIOPreference).where(UserIOPreference.user_id == user_id)
    )
    prefs = result.scalar_one_or_none()
    if not prefs:
        prefs = UserIOPreference(user_id=user_id)
        db.add(prefs)
        await db.flush()
    return prefs


async def update_user_io_preferences(
    db: AsyncSession, user_id: uuid.UUID, data: UserIOPreferenceUpdate
) -> UserIOPreference:
    prefs = await get_user_io_preferences(db, user_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(prefs, field, value)
    await db.flush()
    return prefs
