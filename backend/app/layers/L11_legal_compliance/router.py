"""Layer 11: API endpoints for legal compliance."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth.dependencies import get_current_user
from app.core.auth.models import User
from app.database import get_db
from app.layers.L11_legal_compliance import service
from app.layers.L11_legal_compliance.schemas import (
    ComplianceEvidenceCreate,
    ComplianceEvidenceResponse,
    ComplianceRequirementResponse,
    ComplianceStatusResponse,
)

router = APIRouter()


@router.get("/requirements", response_model=list[ComplianceRequirementResponse])
async def list_requirements(
    framework: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List compliance requirements, optionally filtered by framework."""
    del user
    return await service.list_requirements(db, framework)


@router.get("/status", response_model=ComplianceStatusResponse)
async def get_compliance_status(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get overall compliance status dashboard."""
    del user
    return await service.get_compliance_status(db)


@router.post("/evidence", response_model=ComplianceEvidenceResponse, status_code=201)
async def create_evidence(
    data: ComplianceEvidenceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit compliance evidence for a requirement."""
    return await service.create_evidence(db, data, user.id)


@router.get("/templates")
async def get_regulatory_templates():
    """Get standard regulatory templates for Medizintechnik projects (MDR, ISO 13485, ISO 14971)."""
    from app.layers.L11_legal_compliance.templates import ALL_TEMPLATES
    return {"templates": ALL_TEMPLATES}

