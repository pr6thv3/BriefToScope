from app.config import Settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def init_sentry(settings: Settings) -> None:
    if not settings.sentry_dsn:
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.sentry_environment,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                StarletteIntegration(transaction_style="endpoint"),
                LoggingIntegration(level=None, event_level="ERROR"),
            ],
            traces_sample_rate=0.1,
            send_default_pii=False,
        )
        logger.info("Sentry initialized for backend")
    except Exception as exc:
        logger.warning("Sentry initialization skipped: %s", exc)
