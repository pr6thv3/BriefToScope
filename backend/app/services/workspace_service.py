import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from app.services.storage_service import StorageService
from app.utils.errors import BriefToScopeError, StorageError
from app.utils.logger import get_logger

logger = get_logger(__name__)

_demo_orgs = {}
_demo_members = {}
_demo_invites = {}
_demo_brand_settings = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or f"workspace-{uuid.uuid4().hex[:8]}"


class WorkspaceService:
    """Workspace, membership, invites, and brand settings service.

    Clerk owns identity/session UX; this service mirrors the product tenancy
    state that the backend uses for authorization and billing gates.
    """

    def __init__(self):
        self.storage = StorageService()
        self._demo = self.storage._demo

    async def ensure_default_workspace(self, user: dict) -> dict:
        existing = await self.list_workspaces(user["id"])
        if existing:
            return existing[0]

        workspace_name = _default_workspace_name(user)
        return await self.create_workspace(
            owner_user_id=user["id"],
            name=workspace_name,
            slug=_slugify(workspace_name),
            clerk_org_id="",
        )

    async def create_workspace(
        self,
        owner_user_id: str,
        name: str,
        slug: Optional[str] = None,
        clerk_org_id: str = "",
    ) -> dict:
        org_id = str(uuid.uuid4())
        data = {
            "id": org_id,
            "clerk_org_id": clerk_org_id,
            "name": name,
            "slug": slug or _slugify(name),
            "owner_user_id": owner_user_id,
            "owner_id": owner_user_id,
            "plan": "free",
            "status": "active",
            "created_at": _now(),
            "updated_at": _now(),
        }
        member = {
            "id": str(uuid.uuid4()),
            "org_id": org_id,
            "user_id": owner_user_id,
            "role": "owner",
            "status": "active",
            "created_at": _now(),
            "updated_at": _now(),
        }

        if self._demo:
            _demo_orgs[org_id] = data
            _demo_members[member["id"]] = member
            return {**data, "role": "owner"}

        client = self.storage._get_client()
        try:
            org_resp = client.table("organizations").insert(data).execute()
            client.table("organization_members").insert(member).execute()
            org = org_resp.data[0] if org_resp.data else data
            return {**org, "role": "owner"}
        except Exception as e:
            logger.error("Failed to create workspace: %s", e, exc_info=True)
            raise StorageError("Failed to create workspace")

    async def list_workspaces(self, user_id: str) -> List[dict]:
        if self._demo:
            memberships = [
                m for m in _demo_members.values()
                if m.get("user_id") == user_id and m.get("status") == "active"
            ]
            return [
                {**_demo_orgs[m["org_id"]], "role": m["role"]}
                for m in memberships
                if m.get("org_id") in _demo_orgs
            ]

        client = self.storage._get_client()
        try:
            member_resp = (
                client.table("organization_members")
                .select("*")
                .eq("user_id", user_id)
                .eq("status", "active")
                .execute()
            )
            orgs = []
            for membership in member_resp.data or []:
                org_resp = (
                    client.table("organizations")
                    .select("*")
                    .eq("id", membership["org_id"])
                    .single()
                    .execute()
                )
                if org_resp.data:
                    orgs.append({**org_resp.data, "role": membership["role"]})
            return orgs
        except Exception as e:
            logger.error("Failed to list workspaces: %s", e, exc_info=True)
            return []

    async def get_membership(self, user_id: str, org_id: str) -> Optional[dict]:
        if self._demo:
            return next(
                (
                    m for m in _demo_members.values()
                    if m.get("user_id") == user_id
                    and m.get("org_id") == org_id
                    and m.get("status") == "active"
                ),
                None,
            )

        try:
            resp = (
                self.storage._get_client()
                .table("organization_members")
                .select("*")
                .eq("user_id", user_id)
                .eq("org_id", org_id)
                .eq("status", "active")
                .single()
                .execute()
            )
            return resp.data
        except Exception:
            return None

    async def require_membership(
        self,
        user_id: str,
        org_id: str,
        allowed_roles: Optional[List[str]] = None,
    ) -> dict:
        membership = await self.get_membership(user_id, org_id)
        if not membership:
            raise BriefToScopeError("Not authorized for this workspace", 403)
        if allowed_roles and membership.get("role") not in allowed_roles:
            raise BriefToScopeError("Insufficient workspace permissions", 403)
        return membership

    async def list_members(self, org_id: str) -> List[dict]:
        if self._demo:
            members = [m for m in _demo_members.values() if m.get("org_id") == org_id]
            users = []
            from app.services.storage_service import _demo_users

            for member in members:
                user = _demo_users.get(member["user_id"], {})
                users.append({**member, **{"email": user.get("email", ""), "name": user.get("name", "")}})
            return users

        client = self.storage._get_client()
        resp = client.table("organization_members").select("*").eq("org_id", org_id).execute()
        members = []
        for member in resp.data or []:
            try:
                user_resp = client.table("users").select("*").eq("id", member["user_id"]).single().execute()
                user = user_resp.data or {}
            except Exception:
                user = {}
            members.append({**member, "email": user.get("email", ""), "name": user.get("name", "")})
        return members

    async def create_invite(self, org_id: str, email: str, role: str, invited_by: str) -> dict:
        invite = {
            "id": str(uuid.uuid4()),
            "org_id": org_id,
            "email": email.lower().strip(),
            "role": role,
            "status": "pending",
            "token_hash": uuid.uuid4().hex,
            "invited_by": invited_by,
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "created_at": _now(),
            "updated_at": _now(),
        }
        if self._demo:
            _demo_invites[invite["id"]] = invite
            return invite

        resp = self.storage._get_client().table("invitations").insert(invite).execute()
        return resp.data[0] if resp.data else invite

    async def get_brand_settings(self, org_id: str) -> dict:
        default = {
            "org_id": org_id,
            "logo_url": "",
            "colors_json": {"primary": "#0f172a", "accent": "#2563eb"},
            "footer_text": "Protected against scope creep by BriefToScope AI",
            "pdf_settings_json": {"watermark": True},
            "updated_at": _now(),
        }
        if self._demo:
            return _demo_brand_settings.get(org_id, default)

        try:
            resp = (
                self.storage._get_client()
                .table("brand_settings")
                .select("*")
                .eq("org_id", org_id)
                .single()
                .execute()
            )
            return resp.data or default
        except Exception:
            return default

    async def upsert_brand_settings(self, org_id: str, payload: dict) -> dict:
        data = {
            "org_id": org_id,
            "logo_url": payload.get("logo_url", ""),
            "colors_json": payload.get("colors_json", {}),
            "footer_text": payload.get("footer_text", ""),
            "pdf_settings_json": payload.get("pdf_settings_json", {}),
            "updated_at": _now(),
        }
        if self._demo:
            _demo_brand_settings[org_id] = data
            return data

        resp = self.storage._get_client().table("brand_settings").upsert(data).execute()
        return resp.data[0] if resp.data else data


def _default_workspace_name(user: dict) -> str:
    if user.get("name"):
        return f"{user['name']}'s Workspace"
    if user.get("email"):
        return f"{user['email'].split('@')[0]}'s Workspace"
    return "My Workspace"
