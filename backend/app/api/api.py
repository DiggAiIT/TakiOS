from fastapi import APIRouter
from app.api.endpoints import grade, analyzer
from app.core.auth import router as auth_router
from app.layers.L01_level_selection.router import router as levels_router
from app.layers.L02_tech_units.router import router as tech_units_router
from app.layers.L03_subjects_modules.router import router as subjects_router
from app.layers.L04_content_eselsbruecken.router import router as content_router
from app.layers.L05_knowledge_assessment.router import router as assessment_router
from app.layers.L06_project_creation.router import router as projects_router
from app.layers.L07_faculty_collaboration.router import router as collaboration_router
from app.layers.L08_product_frontend.router import router as frontend_config_router
from app.layers.L09_dimensional_realization.router import router as realization_router
from app.layers.L10_io_definition.router import router as io_router
from app.layers.L11_legal_compliance.router import router as compliance_router
from app.layers.L12_quality_management.router import router as quality_router
from app.layers.L13_social_engineering_impact.router import router as impact_router

api_router = APIRouter()

# Grading
api_router.include_router(grade.router, prefix="/grade", tags=["grading"])

# Auth
api_router.include_router(auth_router.router, prefix="/auth", tags=["auth"])

# Project Analyzer (AI-powered)
api_router.include_router(analyzer.router, prefix="/analyzer", tags=["analyzer"])

# Layer routers
api_router.include_router(levels_router, prefix="/levels", tags=["levels"])
api_router.include_router(tech_units_router, prefix="/tech-units", tags=["tech-units"])
api_router.include_router(subjects_router, prefix="/subjects", tags=["subjects"])
api_router.include_router(content_router, prefix="/content", tags=["content"])
api_router.include_router(assessment_router, prefix="/assessment", tags=["assessment"])
api_router.include_router(projects_router, prefix="/projects", tags=["projects"])
api_router.include_router(collaboration_router, prefix="/collaboration", tags=["collaboration"])
api_router.include_router(frontend_config_router, prefix="/frontend-config", tags=["frontend-config"])
api_router.include_router(realization_router, prefix="/realization", tags=["realization"])
api_router.include_router(io_router, prefix="/io", tags=["io"])
api_router.include_router(compliance_router, prefix="/compliance", tags=["compliance"])
api_router.include_router(quality_router, prefix="/quality", tags=["quality"])
api_router.include_router(impact_router, prefix="/impact", tags=["impact"])

# Agent Team
from app.api.endpoints.agents import router as agents_router

api_router.include_router(agents_router, prefix="/agents", tags=["agents"])

