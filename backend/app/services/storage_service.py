import uuid
from datetime import datetime
from typing import Optional, List
from app.config import get_settings
from app.utils.logger import get_logger
from app.utils.errors import StorageError

logger = get_logger(__name__)

# In-memory stores for demo mode
_demo_users = {}
_demo_projects = {}
_demo_transcripts = {}
_demo_sows = {}
_demo_versions = {}
_demo_esign = {}
_demo_billing = {}


class StorageService:
    def __init__(self):
        self.settings = get_settings()
        self._client = None
        self._demo = self.settings.demo_mode

    def _get_client(self):
        if self._client is None and not self._demo:
            from supabase import create_client, Client
            self._client = create_client(
                self.settings.supabase_url, self.settings.supabase_service_role_key
            )
        return self._client

    async def get_user_by_clerk_id(self, clerk_user_id: str) -> Optional[dict]:
        if self._demo:
            for u in _demo_users.values():
                if u.get("clerk_user_id") == clerk_user_id:
                    return u
            return None
        try:
            resp = self._get_client().table("users").select("*").eq("clerk_user_id", clerk_user_id).single().execute()
            return resp.data
        except Exception:
            return None

    async def create_user(self, clerk_user_id: str, email: str, name: str = "") -> dict:
        data = {
            "id": str(uuid.uuid4()),
            "clerk_user_id": clerk_user_id,
            "email": email,
            "name": name,
            "created_at": datetime.utcnow().isoformat(),
        }
        if self._demo:
            _demo_users[data["id"]] = data
            return data
        try:
            resp = self._get_client().table("users").insert(data).execute()
            return resp.data[0] if resp.data else data
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise StorageError("Failed to create user")

    async def create_project(self, user_id: str, client_name: str, project_name: str, industry: str) -> dict:
        data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "client_name": client_name,
            "project_name": project_name,
            "industry": industry,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        if self._demo:
            _demo_projects[data["id"]] = data
            return data
        try:
            resp = self._get_client().table("projects").insert(data).execute()
            return resp.data[0]
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise StorageError("Failed to create project")

    async def create_transcript(self, project_id: str, raw_text: str, cleaned_text: str, metadata: dict) -> dict:
        data = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "metadata_json": metadata,
            "created_at": datetime.utcnow().isoformat(),
        }
        if self._demo:
            _demo_transcripts[data["id"]] = data
            return data
        try:
            resp = self._get_client().table("transcripts").insert(data).execute()
            return resp.data[0]
        except Exception as e:
            logger.error(f"Failed to create transcript: {e}")
            raise StorageError("Failed to create transcript")

    async def create_sow(self, project_id: str, user_id: str, title: str, content_json: dict,
                         content_markdown: str, risk_flags: list, confidence_score: float) -> dict:
        data = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "user_id": user_id,
            "title": title,
            "content_json": content_json,
            "content_markdown": content_markdown,
            "risk_flags_json": risk_flags,
            "confidence_score": confidence_score,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        if self._demo:
            _demo_sows[data["id"]] = data
            return data
        try:
            resp = self._get_client().table("sows").insert(data).execute()
            return resp.data[0]
        except Exception as e:
            logger.error(f"Failed to create SOW: {e}")
            raise StorageError("Failed to create SOW")

    async def get_sows_by_user(self, user_id: str) -> List[dict]:
        if self._demo:
            return [s for s in _demo_sows.values() if s.get("user_id") == user_id]
        try:
            resp = self._get_client().table("sows").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return resp.data or []
        except Exception as e:
            logger.error(f"Failed to list SOWs: {e}")
            raise StorageError("Failed to list SOWs")

    async def get_sow_by_id(self, sow_id: str) -> Optional[dict]:
        if self._demo:
            return _demo_sows.get(sow_id)
        try:
            resp = self._get_client().table("sows").select("*").eq("id", sow_id).single().execute()
            return resp.data
        except Exception:
            return None

    async def update_sow(self, sow_id: str, content_json: dict, content_markdown: str) -> dict:
        if self._demo:
            s = _demo_sows.get(sow_id)
            if not s:
                raise StorageError("SOW not found")
            s["content_json"] = content_json
            s["content_markdown"] = content_markdown
            s["updated_at"] = datetime.utcnow().isoformat()
            return s
        try:
            data = {
                "content_json": content_json,
                "content_markdown": content_markdown,
                "updated_at": datetime.utcnow().isoformat(),
            }
            resp = self._get_client().table("sows").update(data).eq("id", sow_id).execute()
            return resp.data[0]
        except Exception as e:
            logger.error(f"Failed to update SOW: {e}")
            raise StorageError("Failed to update SOW")

    async def create_sow_version(self, sow_id: str, version_number: int, content_json: dict, content_markdown: str) -> dict:
        data = {
            "id": str(uuid.uuid4()),
            "sow_id": sow_id,
            "version_number": version_number,
            "content_json": content_json,
            "content_markdown": content_markdown,
            "created_at": datetime.utcnow().isoformat(),
        }
        if self._demo:
            _demo_versions[data["id"]] = data
            return data
        try:
            resp = self._get_client().table("sow_versions").insert(data).execute()
            return resp.data[0]
        except Exception as e:
            logger.error(f"Failed to create SOW version: {e}")
            raise StorageError("Failed to create SOW version")

    async def get_sow_versions(self, sow_id: str) -> List[dict]:
        if self._demo:
            return [v for v in _demo_versions.values() if v.get("sow_id") == sow_id]
        try:
            resp = self._get_client().table("sow_versions").select("*").eq("sow_id", sow_id).order("version_number", desc=True).execute()
            return resp.data or []
        except Exception as e:
            logger.error(f"Failed to get SOW versions: {e}")
            return []

    async def update_sow_pdf_url(self, sow_id: str, pdf_url: str) -> dict:
        if self._demo:
            s = _demo_sows.get(sow_id)
            if not s:
                raise StorageError("SOW not found")
            s["pdf_url"] = pdf_url
            s["updated_at"] = datetime.utcnow().isoformat()
            return s
        try:
            data = {"pdf_url": pdf_url, "updated_at": datetime.utcnow().isoformat()}
            resp = self._get_client().table("sows").update(data).eq("id", sow_id).execute()
            return resp.data[0]
        except Exception as e:
            logger.error(f"Failed to update PDF URL: {e}")
            raise StorageError("Failed to update PDF URL")

    async def create_esign_request(self, sow_id: str, provider: str, status: str, signing_url: str, envelope_id: str) -> dict:
        data = {
            "id": str(uuid.uuid4()),
            "sow_id": sow_id,
            "provider": provider,
            "status": status,
            "signing_url": signing_url,
            "envelope_id": envelope_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        if self._demo:
            _demo_esign[data["id"]] = data
            return data
        try:
            resp = self._get_client().table("esign_requests").insert(data).execute()
            return resp.data[0]
        except Exception as e:
            logger.error(f"Failed to create e-sign request: {e}")
            raise StorageError("Failed to create e-sign request")

    async def update_esign_request(self, envelope_id: str, status: str) -> Optional[dict]:
        if self._demo:
            for e in _demo_esign.values():
                if e.get("envelope_id") == envelope_id:
                    e["status"] = status
                    e["updated_at"] = datetime.utcnow().isoformat()
                    return e
            return None
        try:
            data = {"status": status, "updated_at": datetime.utcnow().isoformat()}
            resp = self._get_client().table("esign_requests").update(data).eq("envelope_id", envelope_id).execute()
            return resp.data[0] if resp.data else None
        except Exception as e:
            logger.error(f"Failed to update e-sign request: {e}")
            return None

    async def create_usage_event(self, user_id: str, event_type: str, token_count: int, estimated_cost: float) -> dict:
        data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "event_type": event_type,
            "token_count": token_count,
            "estimated_cost": estimated_cost,
            "created_at": datetime.utcnow().isoformat(),
        }
        if self._demo:
            return data
        try:
            resp = self._get_client().table("usage_events").insert(data).execute()
            return resp.data[0]
        except Exception as e:
            logger.error(f"Failed to log usage event: {e}")
            return data

    async def get_billing_subscription(self, user_id: str) -> Optional[dict]:
        if self._demo:
            for b in _demo_billing.values():
                if b.get("user_id") == user_id:
                    return b
            return None
        try:
            resp = self._get_client().table("billing_subscriptions").select("*").eq("user_id", user_id).single().execute()
            return resp.data
        except Exception:
            return None

    async def upsert_billing_subscription(self, data: dict) -> dict:
        if self._demo:
            _demo_billing[data.get("id", str(uuid.uuid4()))] = data
            return data
        try:
            resp = self._get_client().table("billing_subscriptions").upsert(data).execute()
            return resp.data[0]
        except Exception as e:
            logger.error(f"Failed to upsert billing subscription: {e}")
            raise StorageError("Failed to update billing subscription")

    async def upload_pdf(self, sow_id: str, pdf_bytes: bytes, filename: str) -> str:
        if self._demo:
            return f"https://demo.storage/sow-pdfs/{sow_id}/{filename}"
        try:
            bucket = "sow-pdfs"
            path = f"{sow_id}/{filename}"
            try:
                self._get_client().storage.get_bucket(bucket)
            except Exception:
                self._get_client().storage.create_bucket(bucket, {"public": True})

            self._get_client().storage.from_(bucket).upload(path, pdf_bytes, {"content-type": "application/pdf"})
            url = self._get_client().storage.from_(bucket).get_public_url(path)
            return url
        except Exception as e:
            logger.error(f"Failed to upload PDF: {e}")
            raise StorageError("Failed to upload PDF")
