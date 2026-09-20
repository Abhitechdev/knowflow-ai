"""
Sentry SDK integration for production error tracking.

Initializes only when SENTRY_DSN is set. Scrubs PII fields (user queries,
document content) from event payloads before transmission.
"""
import logging
from typing import Any

logger = logging.getLogger(__name__)

_SCRUB_KEYS = frozenset({
    "query", "content", "text", "chunk", "answer",
    "context", "message", "messages", "password", "token",
    "authorization", "cookie", "secret", "api_key",
})


def _scrub_event(event: dict[str, Any], hint: dict[str, Any]) -> dict[str, Any]:
    """Strip PII / document content from Sentry event payloads."""
    def _redact(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: "[Filtered]" if k.lower() in _SCRUB_KEYS else _redact(v)
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            return [_redact(item) for item in obj]
        return obj

    return _redact(event)  # type: ignore[return-value]


def init_sentry(dsn: str, environment: str, release: str) -> None:
    """Initialize Sentry SDK with PII filtering.

    Args:
        dsn: Sentry Data Source Name (empty string = no-op).
        environment: Deployment environment label (e.g. "production").
        release: Application version string for release tracking.
    """
    if not dsn:
        logger.debug("SENTRY_DSN not set — Sentry integration disabled.")
        return

    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=dsn,
            environment=environment,
            release=release,
            traces_sample_rate=0.1,
            send_default_pii=False,
            before_send=_scrub_event,
        )
        logger.info(f"Sentry initialized for environment={environment} release={release}")
    except ImportError:
        logger.warning("sentry-sdk not installed — skipping Sentry initialization.")
