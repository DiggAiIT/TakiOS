"""Layer 2: Business logic for tech units and chains."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.layers.L02_tech_units.models import TechUnit, TechUnitChain, TechUnitChainLink


async def get_all_units(db: AsyncSession) -> list[TechUnit]:
    result = await db.execute(select(TechUnit))
    return list(result.scalars().all())


async def get_units_by_level(db: AsyncSession, level_id: uuid.UUID) -> list[TechUnit]:
    result = await db.execute(
        select(TechUnit).where(TechUnit.level_id == level_id)
    )
    return list(result.scalars().all())


async def get_chains_by_level(db: AsyncSession, level_id: uuid.UUID) -> list[dict]:
    """Get chains for a level with their ordered tech units."""
    result = await db.execute(
        select(TechUnitChain)
        .where(TechUnitChain.level_id == level_id)
        .options(selectinload(TechUnitChain.links))
    )
    chains = result.scalars().all()

    chain_list = []
    for chain in chains:
        sorted_links = sorted(chain.links, key=lambda l: l.position)
        units = []
        for link in sorted_links:
            unit = await db.get(TechUnit, link.tech_unit_id)
            if unit:
                units.append(unit)
        chain_list.append({
            "id": chain.id,
            "name": chain.name,
            "level_id": chain.level_id,
            "description": chain.description,
            "units": units,
        })
    return chain_list
