from dataclasses import dataclass
from typing import Callable, Iterable

from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings, Settings
from app.utils.errors import AuthError, BriefToScopeError
from app.utils.logger import get_logger
import jwt
from jwt import PyJWKClient

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)

WorkspaceRole = str


@dataclass(frozen=True)
class RequestContext:
    clerk_user_id: str
    email: str
    name: str
    user_id: str
    org_id: str
    role: WorkspaceRole
    plan: str
    subscription_status: str


PERMISSION_ROLES: dict[str, set[str]] = {
    "workspace:manage": {"owner"},
    "members:invite": {"owner", "admin"},
    "billing:manage": {"owner", "admin"},
    "sow:generate": {"owner", "admin", "member"},
    "sow:view": {"owner", "admin", "member", "reviewer"},
    "sow:edit": {"owner", "admin", "member"},
    "sow:export": {"owner", "admin", "member"},
    "sow:esign": {"owner", "admin"},
    "sow:risk_audit": {"owner", "admin", "member", "reviewer"},
}


async def verify_clerk_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    settings: Settings = Depends(get_settings),
) -> dict:
    if settings.demo_mode:
        return {"sub": "demo_user", "email": "demo@example.com"}

    if not credentials:
        raise AuthError("Missing authorization header")

    token = credentials.credentials

    try:
        if not settings.clerk_jwks_url:
            raise AuthError("CLERK_JWKS_URL is required outside DEMO_MODE")

        signing_key = PyJWKClient(settings.clerk_jwks_url).get_signing_key_from_jwt(token)
        decode_kwargs = {
            "algorithms": ["RS256"],
            "options": {"verify_aud": False},
        }
        if settings.clerk_issuer:
            decode_kwargs["issuer"] = settings.clerk_issuer
        claims = jwt.decode(token, signing_key.key, **decode_kwargs)

        return {
            "sub": claims.get("sub", ""),
            "email": claims.get("email") or claims.get("email_address", ""),
            "name": claims.get("name", ""),
            "org_id": claims.get("org_id") or claims.get("o", {}).get("id", ""),
            "role": claims.get("org_role") or claims.get("o", {}).get("rol", ""),
        }
    except Exception as e:
        logger.error("Token verification failed", exc_info=True)
        raise AuthError("Invalid token")


async def get_current_user(token_data: dict = Depends(verify_clerk_token)) -> dict:
    return token_data


async def get_request_context(
    current_user: dict = Depends(get_current_user),
    x_workspace_id: str | None = Header(default=None, alias="X-Workspace-Id"),
) -> RequestContext:
    from app.services.auth_service import AuthService
    from app.services.storage_service import StorageService
    from app.services.workspace_service import WorkspaceService

    user = await AuthService().get_or_create_user(
        current_user["sub"],
        current_user.get("email", ""),
        current_user.get("name", ""),
    )

    workspace_service = WorkspaceService()
    workspaces = await workspace_service.list_workspaces(user["id"])
    if not workspaces:
        workspaces = [await workspace_service.ensure_default_workspace(user)]

    org_id = x_workspace_id or current_user.get("org_id") or workspaces[0]["id"]
    if not any(workspace.get("id") == org_id for workspace in workspaces):
        raise BriefToScopeError("Not authorized for this workspace", 403)

    membership = await workspace_service.require_membership(user["id"], org_id)
    workspace = next((item for item in workspaces if item.get("id") == org_id), workspaces[0])
    subscription = await StorageService().get_billing_subscription(org_id)
    plan = (subscription or {}).get("plan") or workspace.get("plan") or "free"
    subscription_status = (subscription or {}).get("status") or workspace.get("status") or "active"

    return RequestContext(
        clerk_user_id=current_user["sub"],
        email=current_user.get("email", ""),
        name=current_user.get("name", ""),
        user_id=user["id"],
        org_id=org_id,
        role=membership.get("role", "member"),
        plan=plan,
        subscription_status=subscription_status,
    )


def require_roles(allowed_roles: Iterable[str]) -> Callable[[RequestContext], RequestContext]:
    allowed = set(allowed_roles)

    async def dependency(context: RequestContext = Depends(get_request_context)) -> RequestContext:
        if context.role not in allowed:
            raise BriefToScopeError("Insufficient workspace permissions", 403)
        return context

    return dependency


def require_permission(permission: str) -> Callable[[RequestContext], RequestContext]:
    allowed = PERMISSION_ROLES.get(permission, set())

    async def dependency(context: RequestContext = Depends(get_request_context)) -> RequestContext:
        if context.role not in allowed:
            raise BriefToScopeError("Insufficient workspace permissions", 403)
        return context

    return dependency
