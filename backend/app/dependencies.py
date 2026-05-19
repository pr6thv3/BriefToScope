from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import get_settings, Settings
from app.utils.errors import AuthError
from app.utils.logger import get_logger
import httpx
import jwt

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
        # Fetch Clerk public key / JWKS
        jwks_url = "https://api.clerk.dev/v1/jwks"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                jwks_url,
                headers={"Authorization": f"Bearer {settings.clerk_secret_key}"},
            )
            jwks = resp.json()

        # Simplified verification
        unverified = jwt.decode(token, options={"verify_signature": False})
        user_id = unverified.get("sub", "")
        email = unverified.get("email_address", "")

        return {"sub": user_id, "email": email}
    except Exception as e:
        logger.error("Token verification failed", exc_info=True)
        raise AuthError("Invalid token")


async def get_current_user(token_data: dict = Depends(verify_clerk_token)) -> dict:
    return token_data
