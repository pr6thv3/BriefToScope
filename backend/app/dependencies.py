from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings, Settings
from app.utils.errors import AuthError
from app.utils.logger import get_logger
import jwt
from jwt import PyJWKClient

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)


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
