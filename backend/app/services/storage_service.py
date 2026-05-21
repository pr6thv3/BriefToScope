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
_demo_billing_customers = {}
_demo_subscriptions = {}
_demo_webhook_events = {}
_demo_generation_jobs = {}
_demo_generation_job_events = {}


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

    async def create_project(self, user_id: str, client_name: str, project_name: str, industry: str, status: str = "active", org_id: str = "") -> dict:
        data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "created_by": user_id,
            "client_name": client_name,
            "name": project_name,
            "project_name": project_name,
            "industry": industry,
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        if org_id:
            data["org_id"] = org_id
        if self._demo:
            _demo_projects[data["id"]] = data
            return data
        try:
            resp = self._get_client().table("projects").insert(data).execute()
            return resp.data[0]
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise StorageError("Failed to create project")

    async def update_project_status(self, project_id: str, status: str) -> dict:
        if self._demo:
            p = _demo_projects.get(project_id)
            if p:
                p["status"] = status
                p["updated_at"] = datetime.utcnow().isoformat()
                return p
            raise StorageError("Project not found")
        try:
            data = {"status": status, "updated_at": datetime.utcnow().isoformat()}
            resp = self._get_client().table("projects").update(data).eq("id", project_id).execute()
            return resp.data[0] if resp.data else {}
        except Exception as e:
            logger.error(f"Failed to update project status: {e}")
            raise StorageError("Failed to update project status")

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
                         content_markdown: str, risk_flags: list, confidence_score: float, org_id: str = "") -> dict:
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
        if org_id:
            data["org_id"] = org_id
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

    async def get_billing_subscription(self, org_id: str) -> Optional[dict]:
        if self._demo:
            return _demo_subscriptions.get(org_id)
        try:
            resp = self._get_client().table("subscriptions").select("*").eq("org_id", org_id).single().execute()
            return resp.data
        except Exception:
            return None

    async def upsert_billing_subscription(self, data: dict) -> dict:
        if self._demo:
            _demo_subscriptions[data["org_id"]] = data
            return data
        try:
            resp = self._get_client().table("subscriptions").upsert(data, on_conflict="org_id").execute()
            return resp.data[0]
        except Exception as e:
            logger.error(f"Failed to upsert billing subscription: {e}")
            raise StorageError("Failed to update billing subscription")

    async def get_billing_customer_by_paypal_payer_id(self, paypal_payer_id: str) -> Optional[dict]:
        if self._demo:
            for customer in _demo_billing_customers.values():
                if customer.get("paypal_payer_id") == paypal_payer_id:
                    return customer
            return None
        try:
            resp = self._get_client().table("billing_customers").select("*").eq("paypal_payer_id", paypal_payer_id).single().execute()
            return resp.data
        except Exception:
            return None

    async def upsert_billing_customer(self, org_id: str, paypal_payer_id: str) -> dict:
        data = {
            "org_id": org_id,
            "paypal_payer_id": paypal_payer_id,
            "updated_at": datetime.utcnow().isoformat(),
        }
        if self._demo:
            existing = _demo_billing_customers.get(org_id, {})
            data = {"id": existing.get("id", str(uuid.uuid4())), **existing, **data}
            _demo_billing_customers[org_id] = data
            return data
        try:
            resp = self._get_client().table("billing_customers").upsert(data, on_conflict="org_id").execute()
            return resp.data[0]
        except Exception as e:
            logger.error(f"Failed to upsert billing customer: {e}")
            raise StorageError("Failed to update billing customer")

    async def update_organization_plan(self, org_id: str, plan: str, status: str) -> dict:
        data = {"plan": plan, "status": status, "updated_at": datetime.utcnow().isoformat()}
        if self._demo:
            return {"id": org_id, **data}
        try:
            resp = self._get_client().table("organizations").update(data).eq("id", org_id).execute()
            return resp.data[0] if resp.data else {}
        except Exception as e:
            logger.error(f"Failed to update organization plan: {e}")
            raise StorageError("Failed to update organization plan")

    async def record_webhook_event(self, provider: str, event_id: str, event_type: str, payload_json: dict) -> tuple[dict, bool]:
        if self._demo:
            key = f"{provider}:{event_id}"
            if key in _demo_webhook_events:
                return _demo_webhook_events[key], False
            event = {
                "id": str(uuid.uuid4()),
                "provider": provider,
                "event_id": event_id,
                "event_type": event_type,
                "payload_json": payload_json,
                "status": "received",
                "retry_count": 0,
                "created_at": datetime.utcnow().isoformat(),
            }
            _demo_webhook_events[key] = event
            return event, True
        try:
            existing = self._get_client().table("webhook_events").select("*").eq("provider", provider).eq("event_id", event_id).limit(1).execute()
            if existing.data:
                return existing.data[0], False
            data = {
                "provider": provider,
                "event_id": event_id,
                "event_type": event_type,
                "payload_json": payload_json,
                "status": "received",
            }
            resp = self._get_client().table("webhook_events").insert(data).execute()
            return resp.data[0], True
        except Exception as e:
            logger.error(f"Failed to record webhook event: {e}")
            raise StorageError("Failed to record webhook event")

    async def mark_webhook_event(self, provider: str, event_id: str, status: str) -> None:
        data = {"status": status}
        if status in {"processed", "failed", "ignored"}:
            data["processed_at"] = datetime.utcnow().isoformat()
        if self._demo:
            key = f"{provider}:{event_id}"
            if key in _demo_webhook_events:
                _demo_webhook_events[key].update(data)
            return
        try:
            self._get_client().table("webhook_events").update(data).eq("provider", provider).eq("event_id", event_id).execute()
        except Exception as e:
            logger.error(f"Failed to mark webhook event: {e}")

    async def create_generation_job(self, data: dict) -> dict:
        if self._demo:
            _demo_generation_jobs[data["id"]] = data
            return data
        try:
            resp = self._get_client().table("generation_jobs").insert(data).execute()
            return resp.data[0] if resp.data else data
        except Exception as e:
            logger.error(f"Failed to create generation job: {e}")
            raise StorageError("Failed to create generation job")

    async def get_generation_job(self, job_id: str) -> Optional[dict]:
        if self._demo:
            return _demo_generation_jobs.get(job_id)
        try:
            resp = self._get_client().table("generation_jobs").select("*").eq("id", job_id).single().execute()
            return resp.data
        except Exception:
            return None

    async def update_generation_job(self, job_id: str, data: dict) -> dict:
        data["updated_at"] = datetime.utcnow().isoformat()
        if self._demo:
            if job_id not in _demo_generation_jobs:
                raise StorageError("Generation job not found")
            _demo_generation_jobs[job_id].update(data)
            return _demo_generation_jobs[job_id]
        try:
            resp = self._get_client().table("generation_jobs").update(data).eq("id", job_id).execute()
            return resp.data[0] if resp.data else data
        except Exception as e:
            logger.error(f"Failed to update generation job: {e}")
            raise StorageError("Failed to update generation job")

    async def create_generation_job_event(self, generation_job_id: str, event: dict) -> dict:
        data = {
            "generation_job_id": generation_job_id,
            "step": event["step"],
            "status": event["status"],
            "progress": event["progress"],
            "message": event["message"],
            "created_at": event.get("created_at", datetime.utcnow().isoformat()),
        }
        if self._demo:
            _demo_generation_job_events.setdefault(generation_job_id, []).append(data)
            return data
        try:
            resp = self._get_client().table("generation_job_events").insert(data).execute()
            return resp.data[0] if resp.data else data
        except Exception as e:
            logger.error(f"Failed to create generation job event: {e}")
            return data

    async def get_generation_job_events(self, generation_job_id: str) -> List[dict]:
        if self._demo:
            return _demo_generation_job_events.get(generation_job_id, [])
        try:
            resp = self._get_client().table("generation_job_events").select("*").eq("generation_job_id", generation_job_id).order("created_at").execute()
            return resp.data or []
        except Exception as e:
            logger.error(f"Failed to get generation job events: {e}")
            return []

    async def update_sow_status(self, sow_id: str, status: str) -> dict:
        if self._demo:
            s = _demo_sows.get(sow_id)
            if not s:
                raise StorageError("SOW not found")
            s["status"] = status
            s["updated_at"] = datetime.utcnow().isoformat()
            return s
        try:
            data = {"status": status, "updated_at": datetime.utcnow().isoformat()}
            resp = self._get_client().table("sows").update(data).eq("id", sow_id).execute()
            return resp.data[0] if resp.data else {}
        except Exception as e:
            logger.error(f"Failed to update SOW status: {e}")
            raise StorageError("Failed to update SOW status")

    async def upload_pdf(self, sow_id: str, pdf_bytes: bytes, filename: str, user_id: str = "") -> str:
        if self._demo:
            return f"https://demo.storage/sow-pdfs/sows/{user_id or 'demo'}/{sow_id}/{filename}"
        try:
            bucket = "sow-pdfs"
            path = f"sows/{user_id or 'unknown'}/{sow_id}/{filename}"
            try:
                self._get_client().storage.get_bucket(bucket)
            except Exception:
                self._get_client().storage.create_bucket(bucket, {"public": True})

            # Remove existing file if present (overwrite)
            try:
                self._get_client().storage.from_(bucket).remove([path])
            except Exception:
                pass

            self._get_client().storage.from_(bucket).upload(path, pdf_bytes, {"content-type": "application/pdf"})
            url = self._get_client().storage.from_(bucket).get_public_url(path)
            return url
        except Exception as e:
            logger.warning(f"Supabase PDF upload failed: {e}. Returning demo fallback URL.")
            # Fallback to mock URL rather than crashing
            return f"https://demo.storage/sow-pdfs/sows/{user_id or 'unknown'}/{sow_id}/{filename}"

