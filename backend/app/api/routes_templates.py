from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.services.clause_intelligence_service import ClauseIntelligenceService

router = APIRouter(prefix="/api/templates", tags=["Templates"])


@router.get("")
async def list_template_industries(current_user: dict = Depends(get_current_user)):
    return {
        "industries": [
            "Web Design",
            "Branding",
            "SEO",
            "Marketing",
            "Copywriting",
            "Video Production",
            "Consulting",
            "App Development",
            "E-commerce",
            "Social Media",
        ]
    }


@router.get("/{industry}")
async def get_template_intelligence(industry: str, current_user: dict = Depends(get_current_user)):
    return ClauseIntelligenceService().get_scope_intelligence(industry)

