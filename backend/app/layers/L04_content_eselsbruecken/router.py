"""Layer 4: API endpoints for content and Eselsbrücken."""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_db
from app.layers.L04_content_eselsbruecken import service
from app.layers.L04_content_eselsbruecken.schemas import (
    ContentWithBodyResponse,
    GenerateMnemonicRequest,
    MnemonicResponse,
    RateMnemonicRequest,
)

router = APIRouter()


@router.get("/unit/{unit_id}", response_model=ContentWithBodyResponse)
async def get_content(
    unit_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get learning content for a module unit with markdown body and mnemonics."""
    content, body = await service.get_content_with_body(db, unit_id)
    mnemonics = await service.get_mnemonics_for_content(db, content.id, user.id)
    return ContentWithBodyResponse(
        id=content.id,
        module_unit_id=content.module_unit_id,
        body_markdown=body,
        mnemonics=mnemonics,
    )


@router.get("/unit/{unit_id}/mnemonics", response_model=list[MnemonicResponse])
async def get_mnemonics(
    unit_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get mnemonics for a module unit's content."""
    content = await service.get_content_for_unit(db, unit_id)
    return await service.get_mnemonics_for_content(db, content.id, user.id)


@router.post("/mnemonics/generate", response_model=MnemonicResponse, status_code=201)
async def generate_mnemonic(
    data: GenerateMnemonicRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Generate a personalized Eselsbrücke using AI (Maßschneidung)."""
    return await service.generate_mnemonic(
        db, data.content_id, user.id, data.mnemonic_type, data.language, data.project_context
    )


@router.post("/mnemonics/{mnemonic_id}/rate", response_model=MnemonicResponse)
async def rate_mnemonic(
    mnemonic_id: uuid.UUID,
    data: RateMnemonicRequest,
    db: AsyncSession = Depends(get_db),
):
    """Rate the effectiveness of a mnemonic."""
    return await service.rate_mnemonic(db, mnemonic_id, data.score)
