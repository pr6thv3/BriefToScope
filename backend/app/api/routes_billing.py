from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import RequestContext, require_permission
from app.models.production_schemas import (
    BillingActionResponse,
    BillingPlanResponse,
    BillingStatusResponse,
    ChangePlanRequest,
    CheckoutRequest,
    CheckoutResponse,
    UsageSummaryResponse,
)
from app.services.billing_service import BillingService
from app.utils.errors import BriefToScopeError

router = APIRouter(prefix="/api/billing", tags=["Billing"])


@router.get("/plans", response_model=list[BillingPlanResponse])
async def list_billing_plans():
    return BillingService().list_plans()


@router.get("/status", response_model=BillingStatusResponse)
async def get_billing_status(
    context: RequestContext = Depends(require_permission("billing:manage")),
):
    return await BillingService().get_billing_status(context.org_id, context.plan)


@router.get("/usage", response_model=UsageSummaryResponse)
async def get_usage_summary(context: RequestContext = Depends(require_permission("sow:view"))):
    return await BillingService().get_usage_summary(context.org_id, context.user_id, context.plan)


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    req: CheckoutRequest,
    context: RequestContext = Depends(require_permission("billing:manage")),
):
    try:
        return await BillingService().create_checkout_session(
            context.org_id,
            req.plan,
            req.success_url,
            req.cancel_url,
        )
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/change-plan", response_model=BillingActionResponse)
async def change_plan(
    req: ChangePlanRequest,
    context: RequestContext = Depends(require_permission("billing:manage")),
):
    try:
        checkout = await BillingService().change_plan(
            context.org_id,
            req.plan,
            req.success_url,
            req.cancel_url,
        )
        return {"status": "approval_required", "checkout_url": checkout.get("checkout_url")}
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/cancel", response_model=BillingActionResponse)
async def cancel_subscription(context: RequestContext = Depends(require_permission("billing:manage"))):
    try:
        return await BillingService().cancel_subscription(context.org_id)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/reactivate", response_model=BillingActionResponse)
async def reactivate_subscription(context: RequestContext = Depends(require_permission("billing:manage"))):
    try:
        return await BillingService().reactivate_subscription(context.org_id)
    except BriefToScopeError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
