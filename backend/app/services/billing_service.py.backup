import base64
import zlib
from datetime import datetime, timezone
from typing import Dict, List, Optional
from urllib.parse import urlparse

import httpx
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from app.config import get_settings
from app.models.production_schemas import BillingPlanResponse, PlanFeature
from app.services.storage_service import StorageService
from app.utils.logger import get_logger

logger = get_logger(__name__)


PLAN_LIMITS: Dict[str, dict] = {
    "free": {
        "name": "Free",
        "price_monthly": 0,
        "included_sows": 3,
        "included_pdf_exports": 3,
        "included_esign_requests": 0,
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
        "included_pdf_exports": 30,
        "included_esign_requests": 0,
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
        "included_pdf_exports": 100,
        "included_esign_requests": 25,
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
        "included_pdf_exports": 300,
        "included_esign_requests": 100,
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
        "included_pdf_exports": 999999,
        "included_esign_requests": 999999,
        "included_seats": 999999,
        "pdf_export": True,
        "esign": True,
        "watermark": False,
        "features": ["SSO", "Custom retention", "SLA"],
    },
}


class BillingService:
    """PayPal subscription billing and usage gate facade."""

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
        subscription = await self.storage.get_billing_subscription(org_id)
        active_plan = subscription.get("plan", plan) if subscription else plan
        from app.services.usage_service import UsageService

        return await UsageService().get_usage_summary(org_id, active_plan)

    async def get_billing_status(self, org_id: str, plan: str = "free") -> dict:
        subscription = await self.storage.get_billing_subscription(org_id) or {}
        active_plan = subscription.get("plan") or plan
        limits = PLAN_LIMITS.get(active_plan, PLAN_LIMITS["free"])
        usage = await self.get_usage_summary(org_id, "", active_plan)
        status = subscription.get("status") or "active"
        return {
            "plan": active_plan,
            "status": status,
            "renewal_date": subscription.get("current_period_end") or subscription.get("updated_at"),
            "cancel_at_period_end": bool(subscription.get("cancel_at_period_end", False)),
            "seat_quantity": subscription.get("seat_quantity") or limits["included_seats"],
            "usage": usage,
            "limits": limits,
            "available_actions": self._available_actions(active_plan, status),
        }

    async def create_checkout_session(self, org_id: str, plan: str, success_url: str, cancel_url: str) -> dict:
        if self.settings.demo_mode or not self.settings.paypal_client_id or not self.settings.paypal_client_secret:
            return {
                "checkout_url": f"{success_url}?demo_checkout=1&provider=paypal&plan={plan}&org_id={org_id}",
                "demo_mode": True,
            }

        paypal_plan_id = self._paypal_plan_id_for_plan(plan)
        if not paypal_plan_id:
            from app.utils.errors import BriefToScopeError

            raise BriefToScopeError(f"PayPal plan ID is not configured for {plan}", 400)

        access_token = await self._get_access_token()
        payload = {
            "plan_id": paypal_plan_id,
            "custom_id": org_id,
            "application_context": {
                "brand_name": "BriefToScope",
                "locale": "en-US",
                "shipping_preference": "NO_SHIPPING",
                "user_action": "SUBSCRIBE_NOW",
                "return_url": success_url,
                "cancel_url": cancel_url,
            },
        }
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{self._base_url()}/v1/billing/subscriptions",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                json=payload,
            )
            resp.raise_for_status()
            subscription = resp.json()

        await self.storage.upsert_billing_subscription(
            {
                "org_id": org_id,
                "paypal_subscription_id": subscription.get("id"),
                "paypal_plan_id": paypal_plan_id,
                "plan": plan,
                "status": "approval_pending",
                "seat_quantity": PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])["included_seats"],
                "cancel_at_period_end": False,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        approve_url = self._find_link(subscription, "approve")
        return {
            "checkout_url": approve_url or subscription.get("links", [{}])[0].get("href", success_url),
            "demo_mode": False,
        }

    async def change_plan(self, org_id: str, plan: str, success_url: str, cancel_url: str) -> dict:
        return await self.create_checkout_session(org_id, plan, success_url, cancel_url)

    async def cancel_subscription(self, org_id: str) -> dict:
        subscription = await self.storage.get_billing_subscription(org_id)
        if not subscription or not subscription.get("paypal_subscription_id"):
            return {"status": "no_subscription", "message": "No active PayPal subscription is attached."}

        if self.settings.demo_mode or not self.settings.paypal_client_id:
            subscription["status"] = "canceled"
            subscription["cancel_at_period_end"] = True
            await self.storage.upsert_billing_subscription(subscription)
            await self.storage.update_organization_plan(org_id, "free", "active")
            return {"status": "canceled", "message": "Subscription canceled."}

        access_token = await self._get_access_token()
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{self._base_url()}/v1/billing/subscriptions/{subscription['paypal_subscription_id']}/cancel",
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json={"reason": "Customer requested cancellation from BriefToScope billing settings."},
            )
            resp.raise_for_status()
        subscription["status"] = "canceled"
        subscription["cancel_at_period_end"] = True
        await self.storage.upsert_billing_subscription(subscription)
        await self.storage.update_organization_plan(org_id, "free", "active")
        return {"status": "canceled", "message": "Subscription canceled."}

    async def reactivate_subscription(self, org_id: str) -> dict:
        subscription = await self.storage.get_billing_subscription(org_id)
        if not subscription or not subscription.get("paypal_subscription_id"):
            return {"status": "no_subscription", "message": "No PayPal subscription is attached."}

        if self.settings.demo_mode or not self.settings.paypal_client_id:
            subscription["status"] = "active"
            subscription["cancel_at_period_end"] = False
            await self.storage.upsert_billing_subscription(subscription)
            await self.storage.update_organization_plan(org_id, subscription.get("plan", "free"), "active")
            return {"status": "active", "message": "Subscription reactivated."}

        access_token = await self._get_access_token()
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{self._base_url()}/v1/billing/subscriptions/{subscription['paypal_subscription_id']}/activate",
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json={"reason": "Customer requested reactivation from BriefToScope billing settings."},
            )
            resp.raise_for_status()
        subscription["status"] = "active"
        subscription["cancel_at_period_end"] = False
        await self.storage.upsert_billing_subscription(subscription)
        await self.storage.update_organization_plan(org_id, subscription.get("plan", "free"), "active")
        return {"status": "active", "message": "Subscription reactivated."}

    async def handle_paypal_webhook(self, event: dict, headers: dict, raw_body: bytes) -> dict:
        if not self.settings.demo_mode:
            await self._verify_paypal_webhook(headers, raw_body)

        event_id = event.get("id") or headers.get("paypal-transmission-id") or f"paypal-{datetime.now(timezone.utc).timestamp()}"
        event_type = event.get("event_type", "")
        _, inserted = await self.storage.record_webhook_event("paypal", event_id, event_type, event)
        if not inserted:
            return {"status": "ignored", "reason": "duplicate", "event_id": event_id}

        try:
            result = await self._reconcile_paypal_event(event)
            await self.storage.mark_webhook_event("paypal", event_id, "processed")
            return {"status": "processed", "event_id": event_id, **result}
        except Exception:
            await self.storage.mark_webhook_event("paypal", event_id, "failed")
            raise

    def assert_feature_allowed(self, plan: str, feature: str) -> None:
        limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
        if feature == "esign" and not limits["esign"]:
            from app.utils.errors import BriefToScopeError

            raise BriefToScopeError("E-signature is not available on this plan", 402)
        if feature == "pdf_export" and not limits["pdf_export"]:
            from app.utils.errors import BriefToScopeError

            raise BriefToScopeError("PDF export is not available on this plan", 402)

    def _available_actions(self, plan: str, status: str) -> list[str]:
        actions = ["upgrade"]
        if plan != "free":
            actions.extend(["change_plan", "cancel"])
        if status in {"canceled", "suspended", "past_due"}:
            actions.append("reactivate")
        return actions

    async def _reconcile_paypal_event(self, event: dict) -> dict:
        event_type = event.get("event_type", "")
        resource = event.get("resource", {}) or {}

        if event_type.startswith("BILLING.SUBSCRIPTION."):
            return await self._sync_subscription_event(event_type, resource)

        if event_type in {
            "PAYMENT.SALE.COMPLETED",
            "PAYMENT.SALE.DENIED",
            "PAYMENT.SALE.REFUNDED",
            "PAYMENT.SALE.REVERSED",
        }:
            return await self._sync_payment_event(event_type, resource)

        return {"event_type": event_type, "billing_event": "ignored"}

    async def _sync_payment_event(self, event_type: str, resource: dict) -> dict:
        subscription_id = resource.get("billing_agreement_id") or resource.get("subscription_id")
        if not subscription_id:
            return {"event_type": event_type, "billing_event": "payment_recorded"}

        subscription = await self.storage.get_billing_subscription_by_paypal_id(subscription_id)
        if not subscription:
            return {"event_type": event_type, "billing_event": "subscription_not_found"}

        if event_type == "PAYMENT.SALE.COMPLETED":
            subscription["status"] = "active"
            org_status = "active"
        elif event_type in {"PAYMENT.SALE.DENIED", "PAYMENT.SALE.REVERSED"}:
            subscription["status"] = "past_due"
            org_status = "past_due"
        else:
            subscription["status"] = "suspended"
            org_status = "past_due"

        await self.storage.upsert_billing_subscription(subscription)
        await self.storage.update_organization_plan(
            subscription["org_id"],
            subscription.get("plan", "free") if subscription["status"] == "active" else "free",
            org_status,
        )
        return {"event_type": event_type, "billing_event": "payment_synced", "subscription_id": subscription_id}

    async def _sync_subscription_event(self, event_type: str, resource: dict) -> dict:
        subscription_id = resource.get("id") or resource.get("billing_agreement_id")
        paypal_plan_id = resource.get("plan_id", "")
        payer_id = (resource.get("subscriber") or {}).get("payer_id", "")
        org_id = resource.get("custom_id", "")

        if not org_id and payer_id:
            customer = await self.storage.get_billing_customer_by_paypal_payer_id(payer_id)
            org_id = customer.get("org_id", "") if customer else ""

        if not org_id:
            return {"event_type": event_type, "billing_event": "missing_org_mapping", "subscription_id": subscription_id}

        if payer_id:
            await self.storage.upsert_billing_customer(org_id, payer_id)

        status = self._normalize_paypal_subscription_status(event_type, resource.get("status", ""))
        plan = self._plan_for_paypal_plan_id(paypal_plan_id)
        if status in {"canceled", "expired", "suspended"}:
            org_status = "past_due" if status == "suspended" else "active"
        else:
            org_status = "active"

        subscription = {
            "org_id": org_id,
            "paypal_subscription_id": subscription_id,
            "paypal_plan_id": paypal_plan_id,
            "plan": plan,
            "status": status,
            "seat_quantity": PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])["included_seats"],
            "cancel_at_period_end": status in {"canceled", "expired"},
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.storage.upsert_billing_subscription(subscription)
        await self.storage.update_organization_plan(org_id, plan if status == "active" else "free", org_status)
        return {"event_type": event_type, "billing_event": "subscription_synced", "subscription_id": subscription_id, "org_id": org_id}

    async def _verify_paypal_webhook(self, headers: dict, raw_body: bytes) -> None:
        webhook_id = self.settings.paypal_webhook_id
        if not webhook_id:
            from app.utils.errors import BriefToScopeError

            raise BriefToScopeError("PAYPAL_WEBHOOK_ID is required for production webhook verification", 500)

        cert_url = headers.get("paypal-cert-url", "")
        self._validate_paypal_cert_url(cert_url)
        transmission_id = headers.get("paypal-transmission-id", "")
        transmission_time = headers.get("paypal-transmission-time", "")
        transmission_sig = headers.get("paypal-transmission-sig", "")
        if not transmission_id or not transmission_time or not transmission_sig:
            from app.utils.errors import BriefToScopeError

            raise BriefToScopeError("Missing PayPal webhook signature headers", 400)

        crc = zlib.crc32(raw_body) & 0xFFFFFFFF
        message = f"{transmission_id}|{transmission_time}|{webhook_id}|{crc}"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(cert_url)
            resp.raise_for_status()
            cert_pem = resp.content

        cert = x509.load_pem_x509_certificate(cert_pem)
        public_key = cert.public_key()
        try:
            public_key.verify(
                base64.b64decode(transmission_sig),
                message.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
        except Exception as exc:
            from app.utils.errors import BriefToScopeError

            raise BriefToScopeError("Invalid PayPal webhook signature", 400) from exc

    async def _get_access_token(self) -> str:
        auth = httpx.BasicAuth(self.settings.paypal_client_id, self.settings.paypal_client_secret)
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                f"{self._base_url()}/v1/oauth2/token",
                auth=auth,
                data={"grant_type": "client_credentials"},
                headers={"Accept": "application/json", "Accept-Language": "en_US"},
            )
            resp.raise_for_status()
            return resp.json()["access_token"]

    def _base_url(self) -> str:
        return "https://api-m.paypal.com" if self.settings.paypal_mode == "live" else "https://api-m.sandbox.paypal.com"

    def _paypal_plan_id_for_plan(self, plan: str) -> str:
        attr = f"paypal_plan_{plan}"
        return getattr(self.settings, attr, "")

    def _plan_for_paypal_plan_id(self, paypal_plan_id: str) -> str:
        for plan in ("solo", "studio", "agency"):
            if paypal_plan_id and paypal_plan_id == self._paypal_plan_id_for_plan(plan):
                return plan
        return "free"

    def _normalize_paypal_subscription_status(self, event_type: str, paypal_status: str) -> str:
        if event_type.endswith(".CREATED"):
            return "approval_pending"
        if event_type.endswith(".CANCELLED"):
            return "canceled"
        if event_type.endswith(".EXPIRED"):
            return "expired"
        if event_type.endswith(".SUSPENDED") or event_type.endswith(".PAYMENT.FAILED"):
            return "suspended"
        if paypal_status.upper() == "APPROVAL_PENDING":
            return "approval_pending"
        if paypal_status.upper() in {"ACTIVE", "APPROVED"}:
            return "active"
        return paypal_status.lower() or "active"

    def _validate_paypal_cert_url(self, cert_url: str) -> None:
        parsed = urlparse(cert_url)
        allowed_hosts = {"api-m.paypal.com", "api-m.sandbox.paypal.com", "api.paypal.com", "api.sandbox.paypal.com"}
        if parsed.scheme != "https" or parsed.hostname not in allowed_hosts:
            from app.utils.errors import BriefToScopeError

            raise BriefToScopeError("Invalid PayPal certificate URL", 400)

    def _find_link(self, payload: dict, rel: str) -> Optional[str]:
        for link in payload.get("links", []):
            if link.get("rel") == rel:
                return link.get("href")
        return None
