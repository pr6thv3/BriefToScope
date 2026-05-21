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
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_solo: str = ""
    stripe_price_studio: str = ""
    stripe_price_agency: str = ""
    docusign_client_id: str = ""
    docusign_client_secret: str = ""
    docusign_account_id: str = ""
    docusign_base_url: str = ""
    frontend_url: str = ""
    backend_url: str = ""
    redis_url: str = ""
    sentry_dsn: str = ""
    posthog_key: str = ""
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    demo_mode: bool = False

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()

