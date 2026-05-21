from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    clerk_secret_key: str = ""
    clerk_jwks_url: str = ""
    clerk_issuer: str = ""
    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    paypal_webhook_id: str = ""
    paypal_mode: str = "sandbox"
    paypal_plan_solo: str = ""
    paypal_plan_studio: str = ""
    paypal_plan_agency: str = ""
    docusign_client_id: str = ""
    docusign_client_secret: str = ""
    docusign_account_id: str = ""
    docusign_base_url: str = ""
    frontend_url: str = ""
    backend_url: str = ""
    redis_url: str = ""
    celery_enabled: bool = False
    celery_result_backend: str = ""
    sentry_dsn: str = ""
    posthog_key: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    rate_limit_requests_per_minute: int = 120
    admin_email_allowlist: str = ""
    demo_mode: bool = False

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def validate_production_settings(settings: Settings) -> None:
    if settings.demo_mode:
        return

    required = {
        "OPENAI_API_KEY": settings.openai_api_key,
        "SUPABASE_URL": settings.supabase_url,
        "SUPABASE_SERVICE_ROLE_KEY": settings.supabase_service_role_key,
        "CLERK_JWKS_URL": settings.clerk_jwks_url,
        "CLERK_ISSUER": settings.clerk_issuer,
        "FRONTEND_URL": settings.frontend_url,
        "BACKEND_URL": settings.backend_url,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        raise RuntimeError(f"Missing required production environment variables: {', '.join(missing)}")


@lru_cache()
def get_settings() -> Settings:
    return Settings()

