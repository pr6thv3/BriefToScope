from datetime import datetime, timezone
from typing import Any, Dict, Tuple

from app.services.billing_service import PLAN_LIMITS
from app.services.storage_service import StorageService
from app.utils.errors import BriefToScopeError
from app.utils.logger import get_logger

logger = get_logger(__name__)

ESTIMATED_COST_PER_1K_TOKENS = 0.005
INACTIVE_BILLING_STATUSES = {"approval_pending", "past_due", "suspended", "canceled", "expired", "unpaid"}
EVENT_LIMIT_KEYS = {
    "sow_generated": "included_sows",
    "pdf_export": "included_pdf_exports",
    "esign_request": "included_esign_requests",
}


class UsageService:
    def __init__(self):
        self.storage = StorageService()

    async def get_usage_summary(self, org_id: str, plan: str) -> dict:
        period_start, period_end = current_billing_period()
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        return {
            "org_id": org_id,
            "plan": plan,
            "sow_generations_used": await self.storage.sum_usage_events(
                org_id, "sow_generated", period_start, period_end
            ),
            "sow_generations_limit": limits["included_sows"],
            "pdf_exports_used": await self.storage.sum_usage_events(
                org_id, "pdf_export", period_start, period_end
            ),
            "pdf_exports_limit": limits["included_pdf_exports"],
            "esign_requests_used": await self.storage.sum_usage_events(
                org_id, "esign_request", period_start, period_end
            ),
            "esign_requests_limit": limits["included_esign_requests"],
            "seats_used": 1,
            "seats_limit": limits["included_seats"],
            "billing_period_start": period_start.isoformat(),
            "billing_period_end": period_end.isoformat(),
        }

    async def assert_quota_available(
        self,
        org_id: str,
        plan: str,
        subscription_status: str,
        event_type: str,
        quantity: int = 1,
    ) -> None:
        if subscription_status in INACTIVE_BILLING_STATUSES:
            raise BriefToScopeError("Subscription is not active. Update billing to continue.", 402)

        limit_key = EVENT_LIMIT_KEYS.get(event_type)
        if not limit_key:
            return

        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        limit = int(limits.get(limit_key, 0))
        if limit <= 0:
            raise BriefToScopeError("This feature is not included in your current plan.", 402)

        period_start, period_end = current_billing_period()
        used = await self.storage.sum_usage_events(org_id, event_type, period_start, period_end)
        if used + quantity > limit:
            raise BriefToScopeError("Monthly quota exhausted for this action.", 402)

    async def track_event(
        self,
        org_id: str,
        user_id: str,
        event_type: str,
        quantity: int = 1,
        token_count: int = 0,
        metadata: Dict[str, Any] | None = None,
    ):
        estimated_cost = (token_count / 1000) * ESTIMATED_COST_PER_1K_TOKENS
        period_start, period_end = current_billing_period()
        try:
            await self.storage.create_usage_event(
                user_id=user_id,
                org_id=org_id,
                event_type=event_type,
                quantity=quantity,
                token_count=token_count,
                estimated_cost=estimated_cost,
                metadata_json=metadata or {},
                billing_period_start=period_start.isoformat(),
                billing_period_end=period_end.isoformat(),
            )
            logger.info("Tracked usage event %s for org %s", event_type, org_id)
        except Exception as e:
            logger.error("Usage tracking failed: %s", e)


def current_billing_period() -> Tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end
