from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings, validate_production_settings
from app.api.routes_generate import router as generate_router
from app.api.routes_auth import router as auth_router
from app.api.routes_workspaces import router as workspaces_router
from app.api.routes_projects import router as projects_router
from app.api.routes_generations import router as generations_router
from app.api.routes_sows import router as sows_router
from app.api.routes_sow_sections import router as sow_sections_router
from app.api.routes_pdf import router as pdf_router
from app.api.routes_esign import router as esign_router
from app.api.routes_templates import router as templates_router
from app.api.routes_billing import router as billing_router
from app.api.routes_admin import router as admin_router
from app.api.routes_webhooks import router as webhooks_router
from app.middleware.security import InMemoryRateLimitMiddleware, SecurityHeadersMiddleware
from app.utils.errors import BriefToScopeError
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("BriefToScope API started (v1.0.0)")
    if settings.demo_mode:
        logger.info("DEMO MODE is enabled — all AI responses and auth are mocked")
    if not settings.demo_mode:
        validate_production_settings(settings)
    yield
    logger.info("BriefToScope API shutting down")


app = FastAPI(
    title="BriefToScope API",
    description="AI scope intelligence backend for agency SOW generation, editing, export, and billing workflows.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS: support Vercel preview and production domains, plus configured FRONTEND_URL
origins = []
if settings.frontend_url:
    origins.append(settings.frontend_url)
# Allow common Vercel patterns
origins += [
    "http://localhost:3000",
    "https://localhost:3000",
]
if settings.demo_mode:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app" if not settings.demo_mode else None,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)
app.add_middleware(InMemoryRateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


@app.exception_handler(BriefToScopeError)
async def brief_to_scope_exception_handler(request, exc: BriefToScopeError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc: Exception):
    logger.exception("Unhandled API error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

app.include_router(generate_router, tags=["Generate"])
app.include_router(auth_router)
app.include_router(workspaces_router)
app.include_router(projects_router)
app.include_router(generations_router)
app.include_router(sows_router, tags=["SOWs"])
app.include_router(sow_sections_router)
app.include_router(pdf_router, tags=["PDF"])
app.include_router(esign_router, tags=["E-Sign"])
app.include_router(templates_router)
app.include_router(billing_router)
app.include_router(admin_router)
app.include_router(webhooks_router, tags=["Webhooks"])
