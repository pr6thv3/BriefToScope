import pytest

from app.config import Settings, validate_production_settings


def test_production_config_fails_clearly_when_required_env_missing():
    with pytest.raises(RuntimeError) as exc:
        validate_production_settings(Settings(demo_mode=False))

    message = str(exc.value)
    assert "Missing required production environment variables" in message
    assert "OPENAI_API_KEY" in message
    assert "PAYPAL_CLIENT_ID" in message
    assert "CLERK_JWKS_URL" in message


def test_demo_mode_skips_production_env_validation():
    validate_production_settings(Settings(demo_mode=True))


def test_celery_enabled_requires_redis_url():
    settings = Settings(
        demo_mode=False,
        openai_api_key="ok",
        supabase_url="https://example.supabase.co",
        supabase_service_role_key="service",
        clerk_jwks_url="https://clerk.example/.well-known/jwks.json",
        clerk_issuer="https://clerk.example",
        clerk_secret_key="secret",
        paypal_client_id="client",
        paypal_client_secret="secret",
        paypal_webhook_id="webhook",
        paypal_plan_solo="solo",
        paypal_plan_studio="studio",
        paypal_plan_agency="agency",
        frontend_url="https://app.brieftoscope.com",
        backend_url="https://api.brieftoscope.com",
        support_email="support@brieftoscope.com",
        celery_enabled=True,
    )

    with pytest.raises(RuntimeError) as exc:
        validate_production_settings(settings)

    assert "REDIS_URL" in str(exc.value)
