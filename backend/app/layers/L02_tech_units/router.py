"""Layer 2: API endpoints for tech units."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.layers.L02_tech_units import service
from app.layers.L02_tech_units.schemas import TechUnitChainResponse, TechUnitResponse

router = APIRouter()


@router.get("/", response_model=list[TechUnitResponse])
async def list_units(
    level_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List tech units, optionally filtered by knowledge level."""
    if level_id:
        return await service.get_units_by_level(db, level_id)
    return await service.get_all_units(db)


@router.get("/chains", response_model=list[TechUnitChainResponse])
async def list_chains(
    level_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """List tech unit chains for a knowledge level with ordered units."""
    return await service.get_chains_by_level(db, level_id)
