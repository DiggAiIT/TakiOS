"""Layer 10: API endpoints for I/O definition."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_db
from app.layers.L10_io_definition import service
from app.layers.L10_io_definition.schemas import (
    IOCapabilityResponse,
    UserIOPreferenceResponse,
    UserIOPreferenceUpdate,
)

router = APIRouter()


@router.get("/capabilities", response_model=list[IOCapabilityResponse])
async def list_capabilities(db: AsyncSession = Depends(get_db)):
    """List all available I/O capabilities."""
    return await service.list_capabilities(db)


@router.get("/preferences", response_model=UserIOPreferenceResponse)
async def get_io_preferences(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get current user's I/O preferences."""
    return await service.get_user_io_preferences(db, user.id)


@router.put("/preferences", response_model=UserIOPreferenceResponse)
async def update_io_preferences(
    data: UserIOPreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update current user's I/O preferences."""
    return await service.update_user_io_preferences(db, user.id, data)
