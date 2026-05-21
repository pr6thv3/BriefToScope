import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.services.storage_service import StorageService
from app.utils.logger import get_logger

logger = get_logger(__name__)
_demo_audit_logs = {}


class AuditLogService:
    """Append-only audit logging for trust-critical workspace activity."""

    def __init__(self):
        self.storage = StorageService()
        self._demo = self.storage._demo

    async def record(
        self,
        *,
        org_id: str,
        actor_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        ip: str = "",
        user_agent: str = "",
    ) -> dict:
        entry = {
            "id": str(uuid.uuid4()),
            "org_id": org_id,
            "actor_id": actor_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "metadata_json": metadata or {},
            "ip": ip,
            "user_agent": user_agent,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        if self._demo:
            _demo_audit_logs[entry["id"]] = entry
            return entry

        try:
            resp = self.storage._get_client().table("audit_logs").insert(entry).execute()
            return resp.data[0] if resp.data else entry
        except Exception as e:
            logger.warning("Audit log write failed: %s", e)
            return entry

