from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
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
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info("BriefToScope API started (v1.0.0)")
    if settings.demo_mode:
        logger.info("DEMO MODE is enabled — all AI responses and auth are mocked")
    yield
    logger.info("BriefToScope API shutting down")


app = FastAPI(
    title="BriefToScope API",
    description="AI-powered Statement of Work generation backend. Set DEMO_MODE=true for hackathon judging.",
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
    "https://*.vercel.app",
]
if settings.demo_mode:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

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
