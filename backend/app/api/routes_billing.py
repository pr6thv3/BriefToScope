from fastapi import APIRouter, Depends, Header, HTTPException

from app.dependencies import get_current_user
from app.models.production_schemas import (
    BillingPlanResponse,
    CheckoutRequest,
    CheckoutResponse,
    UsageSummaryResponse,
)
from app.services.auth_service import AuthService
from app.services.billing_service import BillingService
from app.services.workspace_service import WorkspaceService
from app.utils.errors import BriefToScopeError

router = APIRouter(prefix="/api/billing", tags=["Billing"])


@router.get("/plans", response_model=list[BillingPlanResponse])
async def list_billing_plans():
    return BillingService().list_plans()


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    req: CheckoutRequest,
    current_user: dict = Depends(get_current_user),
    x_workspace_id: str = Header(default=""),
):
    try:
        user = await AuthService().get_or_create_user(current_user["sub"], current_user.get("email", ""), "")
        workspace_service = WorkspaceService()
        workspace = await workspace_service.ensure_default_workspace(user)
        org_id = x_workspace_id or workspace["id"]
        await workspace_service.require_membership(user["id"], org_id, ["owner", "admin"])
        return await BillingService().create_checkout_session(org_id, req.plan, req.success_url, req.cancel_url)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/usage", response_model=UsageSummaryResponse)
async def get_usage_summary(
    current_user: dict = Depends(get_current_user),
    x_workspace_id: str = Header(default=""),
):
    user = await AuthService().get_or_create_user(current_user["sub"], current_user.get("email", ""), "")
    workspace_service = WorkspaceService()
    workspace = await workspace_service.ensure_default_workspace(user)
    org_id = x_workspace_id or workspace["id"]
    plan = workspace.get("plan", "free")
    return await BillingService().get_usage_summary(org_id, user["id"], plan)

