"""Layer 8: API endpoints for frontend preferences."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_db
from app.layers.L08_product_frontend import service
from app.layers.L08_product_frontend.schemas import UserPreferenceResponse, UserPreferenceUpdate

router = APIRouter()


@router.get("/preferences", response_model=UserPreferenceResponse)
async def get_preferences(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get current user's frontend preferences."""
    return await service.get_preferences(db, user.id)


@router.put("/preferences", response_model=UserPreferenceResponse)
async def update_preferences(
    data: UserPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update current user's frontend preferences."""
    return await service.update_preferences(db, user.id, data)
