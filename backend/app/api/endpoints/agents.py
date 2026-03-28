"""API endpoints for the autonomous agent team system."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.memory.schemas import (
    DreamCycleResponse,
    MemoryIndexResponse,
    MemoryIndexLineResponse,
    MemoryStatusResponse,
)
from app.core.memory.service import MemoryService
from app.database import get_db
from app.services.agent_orchestrator import AgentOrchestrator
from app.tasks.dream_motor import async_dream_cycle
from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    """Request body for running an agent task."""

    task: str = Field(..., max_length=10000)
    context: str = Field(default="", max_length=5000)


class AgentRunResponse(BaseModel):
    """Response from an agent task execution."""

    status: str
    agent_name: str
    model_used: str
    session_id: str
    result: str
    token_estimate: int


router = APIRouter()


@router.get("")
async def list_agents():
    """List all registered agent definitions."""
    agents = await AgentOrchestrator.list_agents()
    return {"agents": agents, "count": len(agents)}


@router.post("/{agent_name}/run", response_model=AgentRunResponse)
async def run_agent(
    agent_name: str,
    request: AgentRunRequest,
    db: AsyncSession = Depends(get_db),
):
    """Execute a task using a specific agent."""
    result = await AgentOrchestrator.run_agent(
        db=db,
        agent_name=agent_name,
        task=request.task,
        context=request.context,
    )
    if result.get("error"):
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/dream")
async def trigger_dream_cycle():
    """Manually trigger an AutoDream memory consolidation cycle."""
    result = await async_dream_cycle({})
    return result


@router.get("/memory", response_model=MemoryStatusResponse)
async def get_memory_status(db: AsyncSession = Depends(get_db)):
    """Get memory system status overview."""
    return await MemoryService.get_status(db)


@router.get("/memory/index", response_model=MemoryIndexResponse)
async def get_memory_index(db: AsyncSession = Depends(get_db)):
    """Retrieve the compacted memory index."""
    rows = await MemoryService.get_memory_index(db)
    max_cycle = max((r.dream_cycle for r in rows), default=0)
    lines = [
        MemoryIndexLineResponse(
            id=r.id,
            line_number=r.line_number,
            content=r.content,
            category=r.category,
            dream_cycle=r.dream_cycle,
            created_at=r.created_at,
        )
        for r in rows
    ]
    from app.config import settings

    return MemoryIndexResponse(
        total_lines=len(lines),
        max_lines=settings.max_index_lines,
        dream_cycle=max_cycle,
        lines=lines,
    )
