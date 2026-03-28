"""Layer 11: Business logic for legal compliance tracking."""

import uuid

from sqlalchemy import distinct, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.layers.L11_legal_compliance.models import ComplianceEvidence, ComplianceRequirement
from app.layers.L11_legal_compliance.schemas import ComplianceEvidenceCreate, ComplianceStatusResponse


async def list_requirements(
    db: AsyncSession, framework: str | None = None
) -> list[ComplianceRequirement]:
    stmt = select(ComplianceRequirement)
    if framework:
        stmt = stmt.where(ComplianceRequirement.framework == framework)
    stmt = stmt.order_by(ComplianceRequirement.framework, ComplianceRequirement.clause)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_compliance_status(db: AsyncSession) -> ComplianceStatusResponse:
    total = await db.execute(select(func.count(ComplianceRequirement.id)))
    total_count = total.scalar() or 0

    evidenced = await db.execute(
        select(func.count(distinct(ComplianceEvidence.requirement_id)))
    )
    evidenced_count = evidenced.scalar() or 0

    verified = await db.execute(
        select(func.count(distinct(ComplianceEvidence.requirement_id))).where(
            ComplianceEvidence.verified_at.is_not(None)
        )
    )
    verified_count = verified.scalar() or 0

    pct = (evidenced_count / total_count * 100) if total_count > 0 else 0.0
    return ComplianceStatusResponse(
        total_requirements=total_count,
        evidenced_requirements=evidenced_count,
        verified_requirements=verified_count,
        compliance_percentage=round(pct, 1),
    )


async def create_evidence(
    db: AsyncSession, data: ComplianceEvidenceCreate, user_id: uuid.UUID
) -> ComplianceEvidence:
    evidence = ComplianceEvidence(
        requirement_id=data.requirement_id,
        evidence_type=data.evidence_type,
        description=data.description,
    )
    db.add(evidence)
    await db.flush()
    return evidence
