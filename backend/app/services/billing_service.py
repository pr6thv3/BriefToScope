from datetime import datetime, timezone
from typing import Dict, List

from app.config import get_settings
from app.models.production_schemas import BillingPlanResponse, PlanFeature
from app.services.storage_service import StorageService


PLAN_LIMITS: Dict[str, dict] = {
    "free": {
        "name": "Free",
        "price_monthly": 0,
        "included_sows": 3,
        "included_seats": 1,
        "pdf_export": True,
        "esign": False,
        "watermark": True,
        "features": ["3 SOWs/month", "Watermarked PDF", "Demo risk audit"],
    },
    "solo": {
        "name": "Solo",
        "price_monthly": 29,
        "included_sows": 30,
        "included_seats": 1,
        "pdf_export": True,
        "esign": False,
        "watermark": False,
        "features": ["PDF export", "Basic templates", "Section regeneration"],
    },
    "studio": {
        "name": "Studio",
        "price_monthly": 79,
        "included_sows": 100,
        "included_seats": 5,
        "pdf_export": True,
        "esign": True,
        "watermark": False,
        "features": ["Team workspace", "Brand settings", "DocuSign integration"],
    },
    "agency": {
        "name": "Agency",
        "price_monthly": 199,
        "included_sows": 300,
        "included_seats": 15,
        "pdf_export": True,
        "esign": True,
        "watermark": False,
        "features": ["Advanced risk audit", "Custom templates", "Clause library"],
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 0,
        "included_sows": 999999,
        "included_seats": 999999,
        "pdf_export": True,
        "esign": True,
        "watermark": False,
        "features": ["SSO", "Custom retention", "SLA"],
    },
}


class BillingService:
    """Stripe billing and usage gate facade.

    The MVP uses Checkout Sessions for subscriptions and a demo checkout URL
    when Stripe is not configured.
    """

    def __init__(self):
        self.settings = get_settings()
        self.storage = StorageService()

    def list_plans(self) -> List[BillingPlanResponse]:
        return [
            BillingPlanResponse(
                key=key,
                name=data["name"],
                price_monthly=data["price_monthly"],
                included_sows=data["included_sows"],
                included_seats=data["included_seats"],
                pdf_export=data["pdf_export"],
                esign=data["esign"],
                watermark=data["watermark"],
                features=[PlanFeature(key=f.lower().replace(" ", "_"), label=f) for f in data["features"]],
            )
            for key, data in PLAN_LIMITS.items()
        ]

    async def get_usage_summary(self, org_id: str, user_id: str, plan: str = "free") -> dict:
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        # Demo-safe defaults. Production can aggregate usage_events by current period.
        return {
            "org_id": org_id,
            "plan": plan,
            "sow_generations_used": 0,
            "sow_generations_limit": limits["included_sows"],
            "pdf_exports_used": 0,
            "esign_requests_used": 0,
            "seats_used": 1,
            "seats_limit": limits["included_seats"],
        }

    async def create_checkout_session(self, org_id: str, plan: str, success_url: str, cancel_url: str) -> dict:
        if self.settings.demo_mode or not self.settings.stripe_secret_key:
            return {
                "checkout_url": f"{success_url}?demo_checkout=1&plan={plan}&org_id={org_id}",
                "demo_mode": True,
            }

        import stripe

        stripe.api_key = self.settings.stripe_secret_key
        price_id = self._price_id_for_plan(plan)
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"org_id": org_id, "plan": plan},
        )
        return {"checkout_url": session.url, "demo_mode": False}

    def assert_feature_allowed(self, plan: str, feature: str) -> None:
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        if feature == "esign" and not limits["esign"]:
            from app.utils.errors import BriefToScopeError

            raise BriefToScopeError("E-signature is not available on this plan", 402)
        if feature == "pdf_export" and not limits["pdf_export"]:
            from app.utils.errors import BriefToScopeError

            raise BriefToScopeError("PDF export is not available on this plan", 402)

    def _price_id_for_plan(self, plan: str) -> str:
        attr = f"stripe_price_{plan}"
        return getattr(self.settings, attr, "") or plan

