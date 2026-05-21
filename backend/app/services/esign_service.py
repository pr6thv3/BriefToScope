import uuid
from typing import Optional
from app.config import get_settings
from app.services.storage_service import StorageService
from app.utils.logger import get_logger
from app.utils.errors import BriefToScopeError
import httpx

logger = get_logger(__name__)


class ESignService:
    def __init__(self):
        self.settings = get_settings()
        self.storage = StorageService()

    async def send_signature_request(self, sow_id: str, sow: dict) -> dict:
        if self.settings.demo_mode:
            return await self._demo_send(sow_id, sow)

        if not self.settings.docusign_client_id:
            raise BriefToScopeError("DocuSign is not configured for this environment", 503)

        try:
            return await self._docusign_send(sow_id, sow)
        except Exception as e:
            logger.error(f"DocuSign send failed: {e}")
            raise BriefToScopeError("Failed to send signature request", 502)

    async def _demo_send(self, sow_id: str, sow: dict) -> dict:
        signing_url = f"{self.settings.frontend_url}/demo-sign/{sow_id}"
        envelope_id = f"demo-{uuid.uuid4().hex[:12]}"
        result = await self.storage.create_esign_request(
            sow_id=sow_id,
            provider="demo",
            status="sent",
            signing_url=signing_url,
            envelope_id=envelope_id,
        )
        return {
            "signing_url": signing_url,
            "envelope_id": envelope_id,
            "status": "sent",
        }

    async def _docusign_send(self, sow_id: str, sow: dict) -> dict:
        account_id = self.settings.docusign_account_id
        base_url = self.settings.docusign_base_url or "https://demo.docusign.net/restapi"
        access_token = await self._get_docusign_access_token()

        envelope_payload = {
            "emailSubject": f"Please sign: {sow.get('title', 'Statement of Work')}",
            "documents": [
                {
                    "documentId": "1",
                    "name": "SOW.pdf",
                }
            ],
            "recipients": {
                "signers": [
                    {
                        "email": sow.get("client_email", "client@example.com"),
                        "name": sow.get("client_name", "Client"),
                        "recipientId": "1",
                        "routingOrder": "1",
                    }
                ]
            },
            "status": "sent",
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{base_url}/v2.1/accounts/{account_id}/envelopes",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=envelope_payload,
            )
            resp.raise_for_status()
            data = resp.json()
            envelope_id = data["envelopeId"]
            signing_url = f"{base_url}/signing/start?envelopeId={envelope_id}"

        result = await self.storage.create_esign_request(
            sow_id=sow_id,
            provider="docusign",
            status="sent",
            signing_url=signing_url,
            envelope_id=envelope_id,
        )
        return {
            "signing_url": signing_url,
            "envelope_id": envelope_id,
            "status": "sent",
        }

    async def _get_docusign_access_token(self) -> str:
        raise BriefToScopeError("DocuSign OAuth token exchange is not configured", 503)

    async def handle_webhook(self, event: dict) -> Optional[dict]:
        envelope_id = event.get("data", {}).get("envelopeId", event.get("envelopeId"))
        status = event.get("event", event.get("status", "unknown"))
        if not envelope_id:
            logger.warning("DocuSign webhook missing envelopeId")
            return None
        return await self.storage.update_esign_request(envelope_id, status)
