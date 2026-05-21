import time
import uuid
from collections import defaultdict, deque
from typing import Deque, Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import get_settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        if request.url.scheme == "https":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response


class InMemoryRateLimitMiddleware(BaseHTTPMiddleware):
    """Small per-process guardrail for abusive bursts.

    This is not a replacement for Cloudflare/Upstash rate limiting in production,
    but it prevents accidental unbounded local/API abuse and keeps behavior
    deterministic in tests.
    """

    def __init__(self, app):
        super().__init__(app)
        self.requests: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:
        settings = get_settings()
        if settings.demo_mode or request.url.path in {"/health", "/docs", "/redoc", "/openapi.json"}:
            return await call_next(request)

        limit = max(settings.rate_limit_requests_per_minute, 1)
        now = time.monotonic()
        key = self._key_for(request)
        bucket = self.requests[key]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()

        if len(bucket) >= limit:
            return JSONResponse(
                {"detail": "Rate limit exceeded. Please retry shortly."},
                status_code=429,
                headers={"Retry-After": "60"},
            )

        bucket.append(now)
        return await call_next(request)

    def _key_for(self, request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for", "")
        ip = forwarded_for.split(",")[0].strip() if forwarded_for else (request.client.host if request.client else "unknown")
        auth = request.headers.get("authorization", "")
        return f"{ip}:{auth[-24:] if auth else 'anonymous'}"
