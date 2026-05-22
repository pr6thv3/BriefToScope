from fastapi import APIRouter, Depends

from app.dependencies import RequestContext, require_permission
from app.services.clause_intelligence_service import ClauseIntelligenceService

router = APIRouter(prefix="/api/templates", tags=["Templates"])


@router.get("")
async def list_template_industries(context: RequestContext = Depends(require_permission("sow:view"))):
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
async def get_template_intelligence(
    industry: str,
    context: RequestContext = Depends(require_permission("sow:view")),
):
    return ClauseIntelligenceService().get_scope_intelligence(industry)

